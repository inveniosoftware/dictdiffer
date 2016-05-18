# This file is part of Dictdiffer.
#
# Copyright (C) 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from dictdiffer.conflict import Conflict
from dictdiffer.resolve import (NoFurtherResolutionException, Resolver,
                                UnresolvedConflictsException)


class UnresolvedConflictsExceptionTest(unittest.TestCase):
    def test_content(self):
        e = UnresolvedConflictsException(None)
        self.assertEqual(None, e.content)

    def test_message(self):
        e = UnresolvedConflictsException(None)
        m = ("The unresolved conflicts are stored in the *content* "
             "attribute of this exception or in the "
             "*unresolved_conflicts* attribute of the "
             "dictdiffer.merge.Merger object.")

        self.assertEqual(m, str(e))
        self.assertEqual(m, e.__repr__())
        self.assertEqual(m, e.__str__())


class ResolverTest(unittest.TestCase):
    def test_init(self):
        # Very basic
        r = Resolver({})

        self.assertEqual(r.actions, {})
        self.assertEqual(r.additional_info, None)
        self.assertEqual(r.unresolved_conflicts, [])

        # With additional_info
        r = Resolver({}, {})

        self.assertEqual(r.actions, {})
        self.assertEqual(r.additional_info, {})
        self.assertEqual(r.unresolved_conflicts, [])

    def test_auto_resolve(self):
        r = Resolver({})
        # Sucessful
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 0)])
        c = Conflict(p1, p2)

        self.assertTrue(r._auto_resolve(c))
        self.assertEqual(c.take, 'f')

        # Fail
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 1)])
        c = Conflict(p1, p2)

        self.assertFalse(r._auto_resolve(c))

    def test_find_conflicting_path(self):
        r = Resolver({})

        # A = shortest
        p1 = ('delete', '', [('foo', [])])
        p2 = ('add', 'foo', [(0, 0)])
        c = Conflict(p1, p2)

        self.assertEqual(r._find_conflicting_path(c), ('foo',))

        # Same
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 0)])
        c = Conflict(p1, p2)

        self.assertEqual(r._find_conflicting_path(c), ('foo', 0))

        # B = shortest
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('delete', '', [('foo', [])])
        c = Conflict(p1, p2)

        self.assertEqual(r._find_conflicting_path(c), ('foo',))

    def test_consecutive_slices(self):
        r = Resolver({})

        slices = [['foo', 'bar', 'apple', 'banana'], ['foo', 'bar', 'apple'],
                  ['foo', 'bar'], ['foo']]

        self.assertEqual(list(r._consecutive_slices(['foo',
                                                     'bar',
                                                     'apple',
                                                     'banana'])), slices)

    def test_resolve_conflicts(self):
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 1)])
        c = [Conflict(p1, p2)]

        # KeyError
        r = Resolver({})

        self.assertRaises(UnresolvedConflictsException,
                          r.resolve_conflicts, [p1], [p2], c)

        # Failing action
        r = Resolver({('foo', 0): lambda *args: False})

        self.assertRaises(UnresolvedConflictsException,
                          r.resolve_conflicts, [p1], [p2], c)

        # No further resolution exception
        def no_further(*args):
            raise NoFurtherResolutionException

        r = Resolver({('foo', 0): no_further})
        self.assertRaises(UnresolvedConflictsException,
                          r.resolve_conflicts, [p1], [p2], c)

        # Succesful
        r = Resolver({('foo', 0): lambda *args: True})
        r.resolve_conflicts([p1], [p2], c)

        self.assertEqual(r.unresolved_conflicts, [])

        # Succesful auto resolve
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 0)])
        c = [Conflict(p1, p2)]

        r = Resolver({})
        r.resolve_conflicts([p1], [p2], c)

        self.assertEqual(r.unresolved_conflicts, [])

    def test_manual_resolve_conflicts(self):
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 0)])
        c = Conflict(p1, p2)

        r = Resolver({})
        r.unresolved_conflicts.append(c)

        r.manual_resolve_conflicts(['s'])

        self.assertEqual(c.take, 's')

        # Raise
        r = Resolver({})
        r.unresolved_conflicts.append(c)

        self.assertRaises(UnresolvedConflictsException,
                          r.manual_resolve_conflicts,
                          [])
