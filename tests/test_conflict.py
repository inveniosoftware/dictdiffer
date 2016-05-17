# This file is part of Dictdiffer.
#
# Copyright (C) 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from dictdiffer.conflict import Conflict, ConflictFinder


class ConflictTest(unittest.TestCase):
    def test_init(self):
        p1 = ('add', '', [(0, 0)])
        p2 = ('add', '', [(1, 2)])

        c = Conflict(p1, p2)

        self.assertEqual(c.first_patch, p1)
        self.assertEqual(c.second_patch, p2)
        self.assertEqual(c.take, None)

    def test_take_patch(self):
        p1 = ('add', '', [(1, 1)])
        p2 = ('add', '', [(1, -1)])

        c = Conflict(p1, p2)

        self.assertRaises(Exception, c.take_patch)

        c.take = 'f'
        self.assertEqual(c.take_patch(), p1)

        c.take = 's'
        self.assertEqual(c.take_patch(), p2)


class ConflictFinderTest(unittest.TestCase):
    def test_is_conflict(self):
        # SAME LENGTH NO CONFLICT
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(2, 0)])

        c = ConflictFinder()
        self.assertFalse(c._is_conflict(p1, p2))

        p1 = ('add', 'foo.bar', [(0, 0)])
        p2 = ('add', 'foo.bar', [(2, 0)])

        c = ConflictFinder()
        self.assertFalse(c._is_conflict(p1, p2))

        # SAME LENGTH CONFLICT
        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 0)])

        c = ConflictFinder()
        self.assertTrue(c._is_conflict(p1, p2))

        p1 = ('add', 'foo.bar', [(0, 0)])
        p2 = ('add', 'foo.bar', [(0, 0)])

        c = ConflictFinder()
        self.assertTrue(c._is_conflict(p1, p2))

        # SUPER PATH
        p1 = ('remove', '', [('foo', [])])
        p2 = ('add', 'foo.bar', [(0, 0)])

        c = ConflictFinder()
        self.assertTrue(c._is_conflict(p1, p2))

        p1 = ('add', 'foo.bar', [(0, 0)])
        p2 = ('remove', '', [('foo', [])])

        c = ConflictFinder()
        self.assertTrue(c._is_conflict(p1, p2))

    def test_find_conflicts(self):
        p11 = ('add', 'foo.bar', [(0, 0)])
        p12 = ('add', 'foo', [(0, 0)])

        p21 = ('add', 'foo.bar', [(0, 0)])
        p22 = ('add', 'foo', [(1, 0)])

        conflicts = [Conflict(p11, p21)]

        c = ConflictFinder()
        self.assertEqual(repr(c.find_conflicts([p11, p12], [p21, p22])),
                         repr(conflicts))
