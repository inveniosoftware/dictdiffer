# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from orderedset import OrderedSet

from dictdiffer.unify import contains, take_patches, unify


class UnifyTest(unittest.TestCase):
    def test_contains(self):
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

        conflicts = [(patch1, patch2),
                     (patch3, patch4),
                     (patch5, patch6),
                     (patch9, patch10)]

        self.assertEqual(0, contains(patch1, conflicts))
        self.assertEqual(0, contains(patch2, conflicts))
        self.assertEqual(1, contains(patch3, conflicts))
        self.assertEqual(1, contains(patch4, conflicts))
        self.assertEqual(2, contains(patch5, conflicts))
        self.assertEqual(2, contains(patch6, conflicts))
        self.assertEqual(3, contains(patch9, conflicts))
        self.assertEqual(3, contains(patch10, conflicts))

    def test_take_patches(self):
        patch1 = {'patches': [1, 2, 3], 'take': [0, 1, 2]}
        patch2 = {'patches': [4, 5, 6], 'take': [None, None, None]}

        taken = list(take_patches(patch1, patch2))
        self.assertEqual([1, 2, 3], taken)
        self.assertTrue('taken' in patch1)
        self.assertTrue('taken' in patch2)

        patch1 = {'patches': [1, 2, 3], 'take': [0, 1, 2]}
        patch2 = {'patches': [4, 5, 6], 'take': [0, None, None]}

        taken = take_patches(patch1, patch2)

        self.assertRaises(Exception, list, taken)

        patch1 = {'patches': [1, 2, 3], 'take': [None, 1, None]}
        patch2 = {'patches': [4, 5, 6], 'take': [0, None, None]}

        taken = list(take_patches(patch1, patch2))
        self.assertEqual([4, 2], taken)
        self.assertTrue('taken' in patch1)
        self.assertTrue('taken' in patch2)

    def test_unify(self):
        # TODO: Do we need to test double conflicts?
        patch1 = {'patches': [1, 2, 3], 'take': [0, 1, 2]}
        patch2 = {'patches': [4, 5, 6], 'take': [None, None, None]}

        patch3 = {'patches': [7, 8, 9], 'take': [0, 1, None]}
        patch4 = {'patches': [10, 11, 12], 'take': [None, None, None]}

        patch5 = {'patches': [13, 14, 15], 'take': [None, None, None]}
        patch6 = {'patches': [16, 17, 18], 'take': [0, 1, 2]}

        patch7 = {'patches': [19, 20, 21], 'take': [None, 1, None]}
        patch8 = {'patches': [22, 23, 24], 'take': [0, None, 2]}

        patch9 = {'patches': [25, 26, 27]}
        patch10 = {'patches': [28, 29, 30]}

        patches1 = [patch1, patch3, patch5, patch7, patch9]
        patches2 = [patch2, patch4, patch6, patch8, patch10]

        conflicts = [(patch1, patch2),
                     (patch3, patch4),
                     (patch5, patch6),
                     (patch7, patch8)]

        unified_patches = list(unify(patches1, patches2, conflicts))

        self.assertEqual([1, 2, 3, 7, 8, 16, 17, 18, 22, 20,
                          24, 25, 26, 27, 28, 29, 30], unified_patches)
