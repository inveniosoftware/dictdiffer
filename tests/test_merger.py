# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from orderedset import OrderedSet

from dictdiffer.merger import Indexer, Merger, UnresolvedConflictsException
from dictdiffer.wrappers import PatchWrap


class TestIndexer(unittest.TestCase):
    def test_build_index(self):
        # Regular index
        class Test(object):
            def __init__(self, id):
                self.id = id

        a = Test(1)
        b = Test(2)
        c = Test(3)

        i = Indexer()
        i.build_index([a, b, c], 'test', [['id']])

        self.assertEqual(i.test[1], a)
        self.assertEqual(i.test[2], b)
        self.assertEqual(i.test[3], c)

        # List index
        wraps = [PatchWrap([('add', 'foo', [(0, 0)])],
                           ('foo', OrderedSet([0]))),
                 PatchWrap([('add', 'foo', [(2, 0)])],
                           ('foo', OrderedSet([2])))]

        i = Indexer()
        i.build_index(wraps, 'wraps', [['path']])

        self.assertEqual(i.wraps[('*',)], [wraps[0], wraps[1]])
        self.assertEqual(i.wraps[('foo', '*')], [wraps[0], wraps[1]])
        self.assertEqual(i.wraps[('foo', 0)], [wraps[0]])
        self.assertEqual(i.wraps[('foo', 2)], [wraps[1]])

        self.assertRaises(KeyError, i.wraps.__getitem__, ('foo',))
        self.assertRaises(KeyError, i.wraps.__getitem__, ('foo', 1))


class MergerTest(unittest.TestCase):
    def test_run(self):
        lca = {'changeme': 'Jo'}
        first = {'changeme': 'Joe'}
        second = {'changeme': 'John'}

        m = Merger(lca, first, second, {})

        self.assertRaises(UnresolvedConflictsException, m.run)

    def test_continue_run(self):
        def take_first(conflict, _, __, ___):
            conflict.take = [('f', x) for x
                             in range(len(conflict.first_patch.patches))]
            return True

        lca = {'changeme': 'Jo'}
        first = {'changeme': 'Joe'}
        second = {'changeme': 'John'}

        m = Merger(lca, first, second, {})

        try:
            m.run()
        except UnresolvedConflictsException:
            pass

        m.continue_run([[('f', 0)]])

        self.assertEqual(m.unified_patches,
                         [('change', 'changeme', ('Jo', 'Joe'))])


if __name__ == '__main__':
    unittest.main()
