# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from orderedset import OrderedSet

from dictdiffer.utils import WildcardDict
from dictdiffer.resolve import _find_conflicting_path, _auto_resolve, resolve


class ResolveTest(unittest.TestCase):
    def test_find_conflicting_path(self):
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        self.assertEqual(('authors', 1),
                         _find_conflicting_path(patch1, patch2))

        patch1 = {'path': ('authors', OrderedSet([1, 2, 3]))}
        patch2 = {'path': (OrderedSet(['authors']),)}
        self.assertEqual(('authors',), _find_conflicting_path(patch1, patch2))

    def test_auto_resolve(self):
        patch1 = {'patches': [1, 2, 3]}
        patch2 = {'patches': [1, 2, 3]}
        self.assertTrue(_auto_resolve(patch1, patch2))
        self.assertEqual([0, 1, 2], patch1['take'])
        self.assertEqual([None, None, None], patch2['take'])

        patch1 = {'patches': [1, 2, 3]}
        patch2 = {'patches': [1, 2, 'different']}
        self.assertFalse(_auto_resolve(patch1, patch2))
        self.assertTrue('take' not in patch1)
        self.assertTrue('take' not in patch2)

        patch1 = {'patches': [1, 2, 3]}
        patch2 = {'patches': [1, 2]}
        self.assertFalse(_auto_resolve(patch1, patch2))
        self.assertTrue('take' not in patch1)
        self.assertTrue('take' not in patch2)

    def test_resolve(self):
        patch1 = {'path': ('authors', OrderedSet([1, 2, 3])),
                  'patches': ['apple', 'banana', 'kiwi']}
        patch2 = {'path': ('authors', OrderedSet([1, 2, 3])),
                  'patches': ['apple', 'banana', 'kiwi']}

        patch3 = {'path': ('foo', OrderedSet(['bar'])),
                  'patches': ['John Do']}
        patch4 = {'path': ('foo', OrderedSet(['bar'])),
                  'patches': ['John Doe']}

        patch5 = {'path': ('authors', OrderedSet([7, 8, 9])),
                  'patches': ['grape', 'pineapple', 'pear']}
        patch6 = {'path': ('authors', OrderedSet([9])),
                  'patches': ['mango']}

        patch7 = {'path': (OrderedSet(['apple']),),
                  'patches': [1]}
        patch8 = {'path': (OrderedSet(['banana']),),
                  'patches': [1]}

        patch9 = {'path': (OrderedSet(['utz']),),
                  'patches': [1]}
        patch10 = {'path': (OrderedSet(['utz']),),
                   'patches': [2]}

        patches1 = [patch1, patch3, patch5, patch7, patch9]
        patches2 = [patch2, patch4, patch6, patch8, patch10]

        conflicts = [(patch1, patch2),
                     (patch3, patch4),
                     (patch5, patch6),
                     (patch9, patch10)]

        def take_left(patch1, patch2, patches1, patches2, _):
            patch1['take'] = range(len(patch1['patches']))
            patch2['take'] = [None for _ in range(len(patch1['patches']))]

            return True

        actions = WildcardDict()
        actions[('authors', '*')] = take_left
        actions[('foo', 'bar')] = take_left

        uc = resolve(patches1, patches2, conflicts, actions)

        self.assertEqual([(patch9, patch10)], uc)

        self.assertEqual([0, 1, 2], patch1['take'])
        self.assertEqual([None, None, None], patch2['take'])

        self.assertEqual([0], patch3['take'])
        self.assertEqual([None], patch4['take'])

        self.assertEqual([0, 1, 2], patch5['take'])
        self.assertEqual([None, None, None], patch6['take'])

        self.assertTrue('take' not in patch7)
        self.assertTrue('take' not in patch8)
