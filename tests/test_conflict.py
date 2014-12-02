# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from orderedset import OrderedSet

from dictdiffer.conflict import Conflict, ConflictFinder
from dictdiffer.wrappers import PatchWrap


class ConflictTest(unittest.TestCase):
    def test_init(self):
        p11 = ('add', '', [(0, 0)])
        wp1 = PatchWrap([p11], (OrderedSet([0]),))

        p21 = ('add', '', [(1, 2)])
        wp2 = PatchWrap([p21], (OrderedSet([1]),))

        c = Conflict(wp1, wp2)

        self.assertEqual(c.first_patch, wp1)
        self.assertEqual(c.second_patch, wp2)
        self.assertEqual(c.take, [])
        self.assertFalse(c.handled)

    def test_take_patches(self):
        p11 = ('add', '', [(1, 1)])
        p12 = ('add', '', [(2, 2)])
        p13 = ('add', '', [(3, 3)])
        wp1 = PatchWrap([p11, p12, p13], (OrderedSet([1]),))

        p21 = ('add', '', [(1, -1)])
        p22 = ('add', '', [(2, -2)])
        p23 = ('add', '', [(3, -3)])
        wp2 = PatchWrap([p21, p22, p23], (OrderedSet([1]),))

        c = Conflict(wp1, wp2)

        c.take = [('f', 0), ('f', 1), ('f', 2)]
        self.assertEqual(list(c.take_patches()), [('f', 1, p11),
                                                  ('f', 1, p12),
                                                  ('f', 1, p13)])

        c.take = [('s', 0), ('s', 1), ('s', 2)]
        self.assertEqual(list(c.take_patches()), [('s', 1, p21),
                                                  ('s', 1, p22),
                                                  ('s', 1, p23)])

        c.take = [('f', 0), ('s', 1), ('f', 2)]
        self.assertEqual(list(c.take_patches()), [('f', 1, p11),
                                                  ('s', 1, p22),
                                                  ('f', 1, p13)])

    def test_get_conflict_shift_value(self):
        p11 = ('add', '', [(1, 1)])
        p12 = ('add', '', [(2, 2)])
        p13 = ('add', '', [(3, 3)])
        wp1 = PatchWrap([p11, p12, p13], (OrderedSet([1]),))

        p21 = ('add', '', [(1, -1)])
        p22 = ('add', '', [(2, -2)])
        p23 = ('add', '', [(3, -3)])
        wp2 = PatchWrap([p21, p22, p23], (OrderedSet([1]),))

        c = Conflict(wp1, wp2)

        c.take = []
        self.assertEqual(c.get_conflict_shift_value(), (-3, -3))

        c.take = [('f', 0), ('s', 1)]
        self.assertEqual(c.get_conflict_shift_value(), (-1, -1))

        c.take = [('f', 0)]
        self.assertEqual(c.get_conflict_shift_value(), (-2, -2))

        c.take = [('f', 0), ('f', 1), ('f', 2)]
        self.assertEqual(c.get_conflict_shift_value(), (0, 0))

        c.take = [('s', 0), ('s', 1), ('s', 2)]
        self.assertEqual(c.get_conflict_shift_value(), (0, 0))

        c.take = [('f', 0), ('s', 1), ('f', 2)]
        self.assertEqual(c.get_conflict_shift_value(), (0, 0))


class ConflictFinderTest(unittest.TestCase):
    def test_is_conflict(self):
        # SAME LENGTH NO CONFLICT
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo', [(2, 0)])], ('foo', OrderedSet([2])))

        c = ConflictFinder()
        self.assertFalse(c._is_conflict(pw1, pw2))

        pw1 = PatchWrap([('add', 'foo.bar', [(0, 0)])],
                        ('foo', 'bar', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo.bar', [(2, 0)])],
                        ('foo', 'bar', OrderedSet([2])))

        c = ConflictFinder()
        self.assertFalse(c._is_conflict(pw1, pw2))

        # SAME LENGTH CONFLICT
        pw1 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo', [(0, 0)])], ('foo', OrderedSet([0])))

        c = ConflictFinder()
        self.assertTrue(c._is_conflict(pw1, pw2))

        pw1 = PatchWrap([('add', 'foo.bar', [(0, 0)])],
                        ('foo', 'bar', OrderedSet([0])))
        pw2 = PatchWrap([('add', 'foo.bar', [(0, 0)])],
                        ('foo', 'bar', OrderedSet([0])))

        c = ConflictFinder()
        self.assertTrue(c._is_conflict(pw1, pw2))

        # SUPER PATH
        pw1 = PatchWrap([('delete', '', [('foo', [])])],
                        (OrderedSet(['foo']),))
        pw2 = PatchWrap([('add', 'foo.bar', [(0, 0)])],
                        ('foo', 'bar', OrderedSet([0, 1])))

        c = ConflictFinder()
        self.assertTrue(c._is_conflict(pw1, pw2))

        pw1 = PatchWrap([('add', 'foo.bar', [(0, 0)])],
                        ('foo', 'bar', OrderedSet([0, 1])))
        pw2 = PatchWrap([('delete', '', [('foo', [])])],
                        (OrderedSet(['foo']),))

        c = ConflictFinder()
        self.assertTrue(c._is_conflict(pw1, pw2))

    def test_find_conflicts(self):
        pw11 = PatchWrap([('add', 'foo.bar', [(0, 0)])],
                         ('foo', 'bar', OrderedSet([0])))
        pw12 = PatchWrap([('add', 'foo', [(0, 0)])],
                         ('foo', OrderedSet([0])))

        pw21 = PatchWrap([('add', 'foo.bar', [(0, 0)])],
                         ('foo', 'bar', OrderedSet([0])))
        pw22 = PatchWrap([('add', 'foo', [(1, 0)])],
                         ('foo', OrderedSet([1])))

        conflicts = [Conflict(PatchWrap([('add', 'foo.bar', [(0, 0)])],
                                        ('foo', 'bar', OrderedSet([0]))),
                              PatchWrap([('add', 'foo.bar', [(0, 0)])],
                                        ('foo', 'bar', OrderedSet([0]))))]

        c = ConflictFinder()
        self.assertEqual(repr(c.find_conflicts([pw11, pw12], [pw21, pw22])),
                         repr(conflicts))
