# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from orderedset import OrderedSet

from dictdiffer.conflict import Conflict
from dictdiffer.wrappers import PatchWrap
from dictdiffer.resolve import Resolver, UnresolvedConflictsException


class ResolverTest(unittest.TestCase):
    def test_init(self):
        # Very basic
        r = Resolver([], [], {})

        self.assertEqual(r.first_patches, [])
        self.assertEqual(r.second_patches, [])
        self.assertEqual(r.actions, {})
        self.assertEqual(r.additional_info, None)
        self.assertEqual(r.unresolved_conflicts, [])

        # With additional_info
        r = Resolver([], [], {}, {})

        self.assertEqual(r.first_patches, [])
        self.assertEqual(r.second_patches, [])
        self.assertEqual(r.actions, {})
        self.assertEqual(r.additional_info, {})
        self.assertEqual(r.unresolved_conflicts, [])

    def test_auto_resolve(self):
        r = Resolver([], [], {})
        # Sucessful
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        c = Conflict(pw1, pw2)

        self.assertTrue(r._auto_resolve(c))
        self.assertEqual(c.take, [('f', 0)])

        # Fail
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo', [(0, 1)])], ('foo', OrderedSet([0])))
        c = Conflict(pw1, pw2)

        self.assertFalse(r._auto_resolve(c))

    def test_find_conflicting_path(self):
        r = Resolver([], [], {})

        # A = shortest
        pw1 = PatchWrap([('delete', '', [('foo', [])])],
                        (OrderedSet(['foo']),))
        pw2 = PatchWrap([('add', 'foo', [(0, 0)])],
                        ('foo', OrderedSet([0])))
        c = Conflict(pw1, pw2)

        self.assertEqual(r._find_conflicting_path(c), ('foo',))

        # Same
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        c = Conflict(pw1, pw2)

        self.assertEqual(r._find_conflicting_path(c), ('foo', 0))

        # B = shortest
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])],
                        ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('delete', '', [('foo', [])])],
                        (OrderedSet(['foo']),))
        c = Conflict(pw1, pw2)

        self.assertEqual(r._find_conflicting_path(c), ('foo',))

    def test_consecutive_slices(self):
        r = Resolver([], [], {})

        slices = [['foo', 'bar', 'apple', 'banana'], ['foo', 'bar', 'apple'],
                  ['foo', 'bar'], ['foo']]

        self.assertEqual(list(r._consecutive_slices(['foo',
                                                     'bar',
                                                     'apple',
                                                     'banana'])), slices)

    def test_resolve_conflicts(self):
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo', [(0, 1)])], ('foo', OrderedSet([0])))
        c = [Conflict(pw1, pw2)]

        # KeyError
        r = Resolver([], [], {})

        self.assertRaises(UnresolvedConflictsException, r.resolve_conflicts, c)

        # Failing action
        r = Resolver([], [], {('foo', 0): lambda w, x, y, z: False})

        self.assertRaises(UnresolvedConflictsException, r.resolve_conflicts, c)

        # Succesful
        r = Resolver([], [], {('foo', 0): lambda w, x, y, z: True})
        r.resolve_conflicts(c)

        self.assertEqual(r.unresolved_conflicts, [])

        # Succesful auto resolve
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        c = [Conflict(pw1, pw2)]

        r = Resolver([], [], {})
        r.resolve_conflicts(c)

        self.assertEqual(r.unresolved_conflicts, [])

    def test_manual_resolve_conflicts(self):
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        c = Conflict(pw1, pw2)

        r = Resolver([], [], {})
        r.unresolved_conflicts.append(c)

        r.manual_resolve_conflicts([[('s', 0)]])

        self.assertEqual(c.take, [('s', 0)])

        # Raise
        r = Resolver([], [], {})
        r.unresolved_conflicts.append(c)

        self.assertRaises(UnresolvedConflictsException,
                          r.manual_resolve_conflicts,
                          [])
