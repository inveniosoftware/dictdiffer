# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from orderedset import OrderedSet

from dictdiffer import diff
from dictdiffer.extractors import SequenceExtractor, get_default_extractors
from dictdiffer.wrappers import (Wrapper,
                                 PatchWrap,
                                 BaseWrapper,
                                 DefaultWrapper,
                                 SequenceWrapper)


class WrapperTest(unittest.TestCase):
    def test_init(self):
        w = Wrapper()

        self.assertEqual(type(w.wrappers[dict]), DefaultWrapper)
        self.assertEqual(type(w.wrappers[list]), DefaultWrapper)
        self.assertEqual(type(w.wrappers[set]), DefaultWrapper)
        self.assertEqual(type(w.wrappers['default'][0]), DefaultWrapper)
        self.assertEqual(type(w.wrappers['default'][1]), DefaultWrapper)
        self.assertEqual(type(w.wrappers['default'][2]), DefaultWrapper)

        self.assertTrue(w.try_default)

    def test_wrap(self):
        # Doesn't need too much testing because of wrappers test...
        # So basic test and then check for no NONE
        first = {'deleteme': 'Hello', 'changeme': 'Jo'}
        second = {'changeme': 'Joe', 'addme': [1, 2, 3]}
        diffs = list(diff(first, second))

        wraps = [PatchWrap([('change', 'changeme', ('Jo', 'Joe'))],
                           (OrderedSet(['changeme']),)),
                 PatchWrap([('add', '', [('addme', [1, 2, 3])])],
                           (OrderedSet(['addme']),)),
                 PatchWrap([('remove', '', [('deleteme', 'Hello')])],
                           (OrderedSet(['deleteme']),))]

        w = Wrapper()
        self.assertEqual(str(w.wrap(diffs, first, second)), str(wraps))

        # No Nones
        first = [2, 3, 5]
        second = [0, 1, 2, 3, 4, 5]

        e = get_default_extractors()
        e[list] = SequenceExtractor

        diffs = list(diff(first, second, extractors=e))

        wraps = [PatchWrap([('add', '', [(0, 0)]), ('add', '', [(1, 1)])],
                           (OrderedSet([0]),)),
                 PatchWrap([('add', '', [(4, 4)])], (OrderedSet([2]),))]

        w = Wrapper()
        w.update_wrappers({list: SequenceExtractor})
        self.assertTrue(None not in w.wrap(diffs, first, second))
        self.assertEqual(str(w.wrap(diffs, first, second)), str(wraps))

        # EXPAND
        first = {'deleteme': 'Hello', 'changeme': 'Jo'}
        second = {'changeme': 'Joe', 'addme': [1, 2, 3]}
        diffs = list(diff(first, second, expand=True))

        wraps = [PatchWrap([('change', 'changeme', ('Jo', 'Joe'))],
                           (OrderedSet(['changeme']),)),
                 PatchWrap([('add', '', [('addme', [])])],
                           (OrderedSet(['addme']),)),
                 PatchWrap([('add', 'addme', [(0, 1)])],
                           ('addme', OrderedSet([0]))),
                 PatchWrap([('add', 'addme', [(1, 2)])],
                           ('addme', OrderedSet([1]))),
                 PatchWrap([('add', 'addme', [(2, 3)])],
                           ('addme', OrderedSet([2]))),
                 PatchWrap([('remove', '', [('deleteme', 'Hello')])],
                           (OrderedSet(['deleteme']),))]

        w = Wrapper()
        self.assertEqual(str(w.wrap(diffs, first, second)), str(wraps))

    def test_update_wrapper(self):
        w = Wrapper()

        w.update_wrappers({list: SequenceExtractor})

        self.assertEqual(type(w.wrappers[dict]), DefaultWrapper)
        self.assertEqual(type(w.wrappers[list]), SequenceWrapper)
        self.assertEqual(type(w.wrappers[set]), DefaultWrapper)
        self.assertEqual(type(w.wrappers['default'][0]), DefaultWrapper)
        self.assertEqual(type(w.wrappers['default'][1]), DefaultWrapper)
        self.assertEqual(type(w.wrappers['default'][2]), DefaultWrapper)

    def test_reset_wrapper(self):
        # Change every wrapper, see if they get reset
        w = Wrapper()

        w.wrappers[dict].test = True
        w.wrappers[list].test = True
        w.wrappers[set].test = True
        w.wrappers['default'][0].test = True
        w.wrappers['default'][1].test = True
        w.wrappers['default'][2].test = True

        self.assertTrue(hasattr(w.wrappers[dict], 'test'))
        self.assertTrue(hasattr(w.wrappers[list], 'test'))
        self.assertTrue(hasattr(w.wrappers[set], 'test'))
        self.assertTrue(hasattr(w.wrappers['default'][0], 'test'))
        self.assertTrue(hasattr(w.wrappers['default'][1], 'test'))
        self.assertTrue(hasattr(w.wrappers['default'][2], 'test'))

        w._reset_wrappers()

        self.assertFalse(hasattr(w.wrappers[dict], 'test'))
        self.assertFalse(hasattr(w.wrappers[list], 'test'))
        self.assertFalse(hasattr(w.wrappers[set], 'test'))
        self.assertFalse(hasattr(w.wrappers['default'][0], 'test'))
        self.assertFalse(hasattr(w.wrappers['default'][1], 'test'))
        self.assertFalse(hasattr(w.wrappers['default'][2], 'test'))

    def test_get_wrapper(self):
        w = Wrapper()
        # BY PATH
        d = DefaultWrapper()
        d.id = 0

        w.wrappers[('foo', 'bar')] = d
        self.assertEqual(w._get_wrapper({}, ('foo', 'bar'), dict).id, 0)

        # BY TYPE
        w.wrappers[dict].id = 1
        self.assertEqual(w._get_wrapper({}, ('foo',), dict).id, 1)

        # BY DEFAULT
        class TMP(dict):
            pass

        w.wrappers['default'][0].id = 2
        self.assertEqual(w._get_wrapper(TMP(), ('foo',), TMP).id, 2)


class BaseWrapperTest(unittest.TestCase):
    def test_get_path(self):
        bw = BaseWrapper()

        patch = ('add/delete', '', [('author', 'Bob')])
        self.assertEqual(('author',), bw.get_path(patch))
        patch = ('add/delete', 'authors', [('name', 'Bob')])
        self.assertEqual(('authors', 'name'), bw.get_path(patch))
        patch = ('add/delete', 'foo.bar', [('name', 'Bob')])
        self.assertEqual(('foo', 'bar', 'name'), bw.get_path(patch))
        patch = ('add/delete', ['foo', 1], [('name', 'Bob')])
        self.assertEqual(('foo', 1, 'name'), bw.get_path(patch))

        patch = ('change', 'foo', [('John', 'Bob')])
        self.assertEqual(('foo',), bw.get_path(patch))
        patch = ('change', 'foo.bar', [('John', 'Bob')])
        self.assertEqual(('foo', 'bar'), bw.get_path(patch))
        patch = ('change', ['foo', 'bar'], [('John', 'Bob')])
        self.assertEqual(('foo', 'bar'), bw.get_path(patch))
        patch = ('change', ['foo', 1], [('John', 'Bob')])
        self.assertEqual(('foo', 1), bw.get_path(patch))


class DefaultWrapperTest(unittest.TestCase):
    def test_default_wrapper(self):
        dw = DefaultWrapper()

        patch = ('add/delete', '', [('author', 'Bob')])
        patches = [patch, patch, patch]
        res = repr(PatchWrap([patch], (OrderedSet(['author']),)))
        self.assertEqual(repr(dw.wrap(patch, patches)), res)

        patch = ('add/delete', 'authors', [('name', 'Bob')])
        patches = [patch, patch, patch]
        res = repr(PatchWrap([patch], ('authors', OrderedSet(['name']))))
        self.assertEqual(repr(dw.wrap(patch, patches)), res)


class SequenceWrapperTest(unittest.TestCase):
    def test_is_applicable(self):
        sw = SequenceWrapper()

        class TMP(list):
            pass

        self.assertTrue(sw.is_applicable([]))
        self.assertTrue(sw.is_applicable(TMP()))

        self.assertFalse(sw.is_applicable({}))
        self.assertFalse(sw.is_applicable(set()))
        self.assertFalse(sw.is_applicable(tuple()))
        self.assertFalse(sw.is_applicable('string'))
        self.assertFalse(sw.is_applicable(1))
        self.assertFalse(sw.is_applicable(1.0))

    def test_init(self):
        sw = SequenceWrapper()
        self.assertEqual(sw._checked_patches, [])

    def test_handle_additions(self):
        # Regular
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('add', '', [(0, 0)])
        p2 = ('add', '', [(1, 1)])
        p3 = ('add', '', [(2, 2)])
        p4 = ('add', '', [(3, 3)])

        patches = [p1, p2, p3, p4]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_additions(p1, patches, 0, res, os), 3)
        self.assertEqual(res, [p2, p3, p4])
        self.assertEqual(os, OrderedSet())

        # different action
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('add', '', [(0, 0)])
        p2 = ('add', '', [(1, 1)])
        p3 = ('remove', '', [(2, 2)])
        p4 = ('add', '', [(3, 3)])

        patches = [p1, p2, p3, p4]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_additions(p1, patches, 0, res, os), 1)
        self.assertEqual(res, [p2])
        self.assertEqual(os, OrderedSet())

        # different superpath
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('add', '', [(0, 0)])
        p2 = ('add', '', [(1, 1)])
        p3 = ('add', 'foo', [(2, 2)])
        p4 = ('add', '', [(3, 3)])

        patches = [p1, p2, p3, p4]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_additions(p1, patches, 0, res, os), 1)
        self.assertEqual(res, [p2])
        self.assertEqual(os, OrderedSet())

        # Gap
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('add', '', [(0, 0)])
        p2 = ('add', '', [(1, 1)])
        p3 = ('add', '', [(3, 2)])
        p4 = ('add', '', [(4, 3)])

        patches = [p1, p2, p3, p4]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_additions(p1, patches, 0, res, os), 1)
        self.assertEqual(res, [p2])
        self.assertEqual(os, OrderedSet())

    def test_handle_deletions(self):
        # Regular
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('remove', '', [(3, 0)])
        p2 = ('remove', '', [(2, 1)])
        p3 = ('remove', '', [(1, 2)])
        p4 = ('remove', '', [(0, 3)])

        patches = [p1, p2, p3, p4]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_deletions(p1, patches, 3, res, os), 3)
        self.assertEqual(res, [p2, p3, p4])
        self.assertEqual(os, OrderedSet([2, 1, 0]))

        # different action
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('remove', '', [(3, 0)])
        p2 = ('remove', '', [(2, 1)])
        p3 = ('add', '', [(1, 2)])
        p4 = ('remove', '', [(0, 3)])

        patches = [p1, p2, p3, p4]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_deletions(p1, patches, 3, res, os), 1)
        self.assertEqual(res, [p2])
        self.assertEqual(os, OrderedSet([2]))

        # different superpath
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('remove', '', [(3, 0)])
        p2 = ('remove', '', [(2, 1)])
        p3 = ('remove', 'foo', [(1, 2)])
        p4 = ('remove', '', [(0, 3)])

        patches = [p1, p2, p3, p4]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_deletions(p1, patches, 3, res, os), 1)
        self.assertEqual(res, [p2])
        self.assertEqual(os, OrderedSet([2]))

        # Gap
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('remove', '', [(4, 0)])
        p2 = ('remove', '', [(3, 1)])
        p3 = ('remove', '', [(1, 2)])
        p4 = ('remove', '', [(0, 3)])

        patches = [p1, p2, p3, p4]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_deletions(p1, patches, 4, res, os), 1)
        self.assertEqual(res, [p2])
        self.assertEqual(os, OrderedSet([3]))

    def test_check_next_removes(self):
        # Regular
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('remove', '', [(3, 0)])
        p2 = ('remove', '', [(2, 1)])
        p3 = ('remove', '', [(1, 2)])

        patches = [p1, p2, p3]

        self.assertTrue(sw._check_next_removes(p1, patches, 0))

        # different action
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('remove', '', [(3, 0)])
        p2 = ('remove', '', [(2, 1)])
        p3 = ('add', '', [(1, 2)])

        patches = [p1, p2, p3]

        self.assertTrue(sw._check_next_removes(p1, patches, 1))

        # different superpath
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('remove', '', [(3, 0)])
        p2 = ('remove', '', [(2, 1)])
        p3 = ('remove', 'foo', [(1, 2)])

        patches = [p1, p2, p3]

        self.assertTrue(sw._check_next_removes(p1, patches, 1))

        # Gap
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('remove', '', [(4, 0)])
        p2 = ('remove', '', [(3, 1)])
        p3 = ('remove', '', [(1, 2)])
        p4 = ('remove', '', [(0, 3)])

        patches = [p1, p2, p3, p4]

        self.assertTrue(sw._check_next_removes(p1, patches, 2))

    def test_handle_changes(self):
        # Regular
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('change', [0], [(0, 0)])
        p2 = ('change', [1], [(1, 1)])
        p3 = ('change', [2], [(2, 2)])

        patches = [p1, p2, p3]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_changes(p1, patches, 0, res, os), (0, 0))
        self.assertEqual(res, [p2, p3])
        self.assertEqual(os, OrderedSet([1, 2]))

        # Regular different super path
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('change', [0], [(0, 0)])
        p2 = ('change', [1], [(1, 1)])
        p3 = ('change', ['foo', 2], [(2, 2)])

        patches = [p1, p2, p3]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_changes(p1, patches, 0, res, os), (0, 0))
        self.assertEqual(res, [p2])
        self.assertEqual(os, OrderedSet([1]))

        # Regular gap
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('change', [0], [(0, 0)])
        p2 = ('change', [1], [(1, 1)])
        p3 = ('change', [3], [(2, 2)])

        patches = [p1, p2, p3]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_changes(p1, patches, 0, res, os), (0, 0))
        self.assertEqual(res, [p2])
        self.assertEqual(os, OrderedSet([1]))

        # PLUS ADDITIONS
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('change', [0], (0, 0))
        p2 = ('change', [1], (1, 1))
        p3 = ('change', [2], (2, 2))
        p4 = ('add', '', [(3, 3)])
        p5 = ('add', '', [(4, 4)])

        patches = [p1, p2, p3, p4, p5]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_changes(p1, patches, 0, res, os), (2, 0))
        self.assertEqual(res, [p2, p3, p4, p5])
        self.assertEqual(os, OrderedSet([1, 2, 3]))

        # PLUS DELETIONS
        sw = SequenceWrapper()
        sw.current_superpath = ()
        p1 = ('change', [0], (0, 0))
        p2 = ('change', [1], (1, 1))
        p3 = ('change', [2], (2, 2))
        p4 = ('remove', '', [(4, 4)])
        p5 = ('remove', '', [(3, 3)])

        patches = [p1, p2, p3, p4, p5]

        res = []
        os = OrderedSet()

        self.assertEqual(sw._handle_changes(p1, patches, 0, res, os), (0, 2))
        self.assertEqual(res, [p2, p3, p4, p5])
        self.assertEqual(os, OrderedSet([1, 2, 4, 3]))

    def test_already_checked(self):
        sw = SequenceWrapper()

        sw._checked_patches.append(('author',))
        patch = ('add/delete', '', [('author', 'Bob')])
        self.assertEqual(sw.wrap(patch, None), None)

        sw._checked_patches.append(('authors', 'name'))
        patch = ('add/delete', 'authors', [('name', 'Bob')])
        self.assertEqual(sw.wrap(patch, None), None)

    def test_sequence_wrapper_add(self):
        # The rest
        sw = SequenceWrapper()

        patch1 = ('add', 'authors', [(0, 'Bob')])
        patch2 = ('add', 'authors', [(1, 'Jo')])
        patch3 = ('add', 'authors', [(2, 'Jack')])
        patch4 = ('add', 'authors', [(3, 'John')])

        patches = [patch1, patch2, patch3, patch4]

        res = repr(PatchWrap([patch1, patch2, patch3, patch4],
                             ('authors', OrderedSet([0]))))
        self.assertEqual(repr(sw.wrap(patch1, patches)), res)

        # Test a gap
        sw = SequenceWrapper()

        patch1 = ('add', 'authors', [(0, 'Bob')])
        patch2 = ('add', 'authors', [(1, 'Jo')])
        patch3 = ('add', 'authors', [(3, 'Jack')])
        patch4 = ('add', 'authors', [(4, 'John')])

        patches = [patch1, patch2, patch3, patch4]

        res = repr(PatchWrap([patch1, patch2],
                             ('authors', OrderedSet([0]))))
        self.assertEqual(repr(sw.wrap(patch1, patches)), res)
        res = repr(PatchWrap([patch3, patch4],
                             ('authors', OrderedSet([1]))))
        self.assertEqual(repr(sw.wrap(patch3, patches)), res)

        # different super path
        sw = SequenceWrapper()

        patch1 = ('add', 'authors', [(0, 'Bob')])
        patch2 = ('add', 'authors', [(1, 'Jo')])
        patch3 = ('add', 'foo', [(2, 'Jack')])
        patch4 = ('add', 'bar', [(3, 'John')])

        patches = [patch1, patch2, patch3, patch4]

        res = repr(PatchWrap([patch1, patch2],
                             ('authors', OrderedSet([0]))))
        self.assertEqual(repr(sw.wrap(patch1, patches)), res)
        res = repr(PatchWrap([patch3],
                             ('foo', OrderedSet([2]))))
        self.assertEqual(repr(sw.wrap(patch3, patches)), res)
        res = repr(PatchWrap([patch4],
                             ('bar', OrderedSet([3]))))
        self.assertEqual(repr(sw.wrap(patch4, patches)), res)

    def test_sequence_wrapper_change(self):
        sw = SequenceWrapper()

        patch1 = ('change', ['authors', 0], ('Bab', 'Bob'))
        patch2 = ('change', ['authors', 1], ('Joe', 'Jo'))

        patches = [patch1, patch2]

        res = repr(PatchWrap([patch1, patch2],
                             ('authors', OrderedSet([0, 1]))))
        self.assertEqual(repr(sw.wrap(patch1, patches)), res)

if __name__ == '__main__':
    unittest.main()
