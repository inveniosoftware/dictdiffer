# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from types import GeneratorType
from orderedset import OrderedSet
from dictdiffer.conflict import (_is_conflict, _handle_conflict,
                                 _get_conflicts, get_conflicts,
                                 _get_conflicts_string, print_conflicts)


class ConflictTest(unittest.TestCase):
    def test_is_conflict(self):
        # Conflict same path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        conflict, intersection = _is_conflict(patch1, patch2)
        self.assertTrue(conflict)
        self.assertEqual(OrderedSet([1, 2, 3]), intersection)

        # Conflict similar path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('authors', OrderedSet([2]))}
        conflict, intersection = _is_conflict(patch1, patch2)
        self.assertTrue(conflict)
        self.assertEqual(OrderedSet([2]), intersection)

        # Conflict Super path 1
        patch1 = {'path': (OrderedSet(['authors']),)}
        patch2 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        conflict, intersection = _is_conflict(patch1, patch2)
        self.assertTrue(conflict)
        self.assertEqual(OrderedSet(), intersection)

        # Conflict Super path 2
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': (OrderedSet(['authors']),)}
        conflict, intersection = _is_conflict(patch1, patch2)
        self.assertTrue(conflict)
        self.assertEqual(OrderedSet(), intersection)

        # Different path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('foo', 'bar', OrderedSet([1]))}
        conflict, intersection = _is_conflict(patch1, patch2)
        self.assertFalse(conflict)
        self.assertEqual(OrderedSet(), intersection)

        # Different path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('foo', OrderedSet(['banana', 'apple']))}
        conflict, intersection = _is_conflict(patch1, patch2)
        self.assertFalse(conflict)
        self.assertEqual(OrderedSet(), intersection)

        # Different path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': (OrderedSet(['foo']),)}
        conflict, intersection = _is_conflict(patch1, patch2)
        self.assertFalse(conflict)
        self.assertEqual(OrderedSet(), intersection)

    def test_handle_conflict(self):
        # Conflict same path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        self.assertEqual((patch1, patch2), _handle_conflict(patch1, patch2,
                                                            None, None))

        # Conflict similar path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('authors', OrderedSet([2]))}
        self.assertEqual((patch1, patch2), _handle_conflict(patch1, patch2,
                                                            None, None))

        # Conflict Super path 1
        patch1 = {'path': (OrderedSet(['authors']),)}
        patch2 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        self.assertEqual((patch1, patch2), _handle_conflict(patch1, patch2,
                                                            None, None))

        # Conflict Super path 2
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': (OrderedSet(['authors']),)}
        self.assertEqual((patch1, patch2), _handle_conflict(patch1, patch2,
                                                            None, None))

        # Different path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('foo', 'bar', OrderedSet([1]))}
        self.assertEqual(None, _handle_conflict(patch1, patch2, None, None))

        # Different path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('foo', OrderedSet(['banana', 'apple']))}
        self.assertEqual(None, _handle_conflict(patch1, patch2, None, None))

        # Different path
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': (OrderedSet(['foo']),)}
        self.assertEqual(None, _handle_conflict(patch1, patch2, None, None))

    def test_get_conflicts(self):
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('authors', OrderedSet([1, 2, 3]))}

        patch3 = {'path': ('foo', OrderedSet(['bar']))}
        patch4 = {'path': ('foo', OrderedSet(['bar']))}

        patch5 = {'path': ('authors', OrderedSet([7, 8, 9]))}
        patch6 = {'path': ('authors', OrderedSet([9]))}

        patch7 = {'path': (OrderedSet(['apple']),)}
        patch8 = {'path': (OrderedSet(['banana']),)}

        patches1 = [patch1, patch3, patch5, patch7]
        patches2 = [patch2, patch4, patch6, patch8]

        conflicts = get_conflicts(patches1, patches2)

        self.assertTrue(type(conflicts) == GeneratorType)

        conflicts = list(conflicts)

        self.assertTrue(len(conflicts) == 3)
        self.assertEqual((patch1, patch2), conflicts[0])
        self.assertEqual((patch3, patch4), conflicts[1])
        self.assertEqual((patch5, patch6), conflicts[2])

    def test_get_conflicts_string(self):
        patch1 = {'id': 1,
                  'path': (OrderedSet(['institution']),),
                  'patches': [('remove', '', ('foo', 'banana'))]}
        patch2 = {'id': 2,
                  'path': (OrderedSet(['institution']),),
                  'patches': [('remove', '', ('foo', 'banana'))]}

        patch3 = {'id': 3,
                  'path': ('authors', OrderedSet([0, 1]),),
                  'patches': [('add', 'authors', (0, 'Jack')),
                              ('change', ['authors', 1], ('Jo', 'Joe')),
                              None]}
        patch4 = {'id': 4,
                  'path': ('authors', OrderedSet([1, 2]),),
                  'patches': [None,
                              ('change', ['authors', 1], ('Jo', 'John')),
                              ('add', 'authors', (2, 'Jimmy'))]}
        conflicts = [(patch1, patch2), (patch3, patch4)]

        with open('tests/get_conflicts_string.txt', 'r') as f:
            pt = f.read().strip()

        self.assertEqual(pt, _get_conflicts_string(conflicts))

    def test_print_conflicts(self):
        patch1 = {'id': 1,
                  'path': (OrderedSet(['institution']),),
                  'patches': [('remove', '', ('foo', 'banana'))]}
        patch2 = {'id': 2,
                  'path': (OrderedSet(['institution']),),
                  'patches': [('remove', '', ('foo', 'banana'))]}

        patch3 = {'id': 3,
                  'path': ('authors', OrderedSet([0, 1]),),
                  'patches': [('add', 'authors', (0, 'Jack')),
                              ('change', ['authors', 1], ('Jo', 'Joe')),
                              None]}
        patch4 = {'id': 4,
                  'path': ('authors', OrderedSet([1, 2]),),
                  'patches': [None,
                              ('change', ['authors', 1], ('Jo', 'John')),
                              ('add', 'authors', (2, 'Jimmy'))]}
        conflicts = [(patch1, patch2), (patch3, patch4)]

        print_conflicts(conflicts)
        self.assertTrue(True)
