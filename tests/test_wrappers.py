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
from dictdiffer.wrappers import _prepare_wrappers, wrap, unwrap


class WrapTest(unittest.TestCase):
    def test_prepare_wrappers(self):
        # Default
        wrappers = _prepare_wrappers(None)
        self.assertEqual(1, len(wrappers.keys()))
        self.assertEqual(DefaultWrapper, type(wrappers[('*',)]))

        # Custom without '*'
        wrapper = WildcardDict()
        wrappers = _prepare_wrappers(wrapper)
        self.assertEqual(1, len(wrappers.keys()))
        self.assertEqual(DefaultWrapper, type(wrappers[('*',)]))

        # Custom without '*' and another path
        wrapper = WildcardDict({('foo',): 'bar'})
        wrappers = _prepare_wrappers(wrapper)
        self.assertEqual(2, len(wrappers.keys()))
        self.assertEqual(DefaultWrapper, type(wrappers[('*',)]))
        self.assertEqual('bar', wrappers[('foo',)])

        # Complete custom
        wrapper = WildcardDict({('*',): DefaultWrapper(),
                                ('foo',): 'bar'})
        wrappers = _prepare_wrappers(wrapper)
        self.assertEqual(2, len(wrappers.keys()))
        self.assertEqual(DefaultWrapper, type(wrappers[('*',)]))
        self.assertEqual('bar', wrappers[('foo',)])

    def test_wrap(self):
        patch1 = ('add', 'authors', [(0, 'Bob')])
        patch2 = ('add', 'authors', [(1, 'Jo')])
        patch3 = ('add', 'authors', [(2, 'Jack')])
        patch4 = ('add', 'authors', [(3, 'John')])

        patches1 = [patch1, patch2, patch3, patch4]

        patch5 = ('add', 'foo', [(0, 'Bob')])
        patch6 = ('add', 'foo', [(1, 'Jo')])
        patch7 = ('add', 'foo', [(2, 'Jack')])
        patch8 = ('add', 'foo', [(3, 'John')])

        patches2 = [patch5, patch6, patch7, patch8]

        # Default wrap
        res = [{'patches': [('add', 'authors', [(0, 'Bob')])],
                'path': ('authors', OrderedSet([0]))},
               {'patches': [('add', 'authors', [(1, 'Jo')])],
                'path': ('authors', OrderedSet([1]))},
               {'patches': [('add', 'authors', [(2, 'Jack')])],
                'path': ('authors', OrderedSet([2]))},
               {'patches': [('add', 'authors', [(3, 'John')])],
                'path': ('authors', OrderedSet([3]))}]

        self.assertEqual(res, list(wrap(patches1)))

        # SequenceWrapper
        res = [{'patches': [('add', 'authors', [(0, 'Bob')]),
                            ('add', 'authors', [(1, 'Jo')]),
                            ('add', 'authors', [(2, 'Jack')]),
                            ('add', 'authors', [(3, 'John')])],
                'path': ('authors', OrderedSet([0, 1, 2, 3]))}]

        wrapper = WildcardDict({('*',): SequenceWrapper()})

        self.assertEqual(res, list(wrap(patches1, wrapper)))

        # Mixed
        res = [{'patches': [('add', 'authors', [(0, 'Bob')]),
                            ('add', 'authors', [(1, 'Jo')]),
                            ('add', 'authors', [(2, 'Jack')]),
                            ('add', 'authors', [(3, 'John')])],
                'path': ('authors', OrderedSet([0, 1, 2, 3]))},
               {'patches': [('add', 'foo', [(0, 'Bob')])],
                'path': ('foo', OrderedSet([0]))},
               {'patches': [('add', 'foo', [(1, 'Jo')])],
                'path': ('foo', OrderedSet([1]))},
               {'patches': [('add', 'foo', [(2, 'Jack')])],
                'path': ('foo', OrderedSet([2]))},
               {'patches': [('add', 'foo', [(3, 'John')])],
                'path': ('foo', OrderedSet([3]))}]

        wrapper = WildcardDict({('authors', '*'): SequenceWrapper()})

        self.assertEqual(res, list(wrap(patches1+patches2, wrapper)))

    def test_unwrap(self):
        patch1 = ('add', 'authors', [(0, 'Bob')])
        patch2 = ('add', 'authors', [(1, 'Jo')])
        patch3 = ('add', 'authors', [(2, 'Jack')])
        patch4 = ('add', 'authors', [(3, 'John')])

        patches1 = [patch1, patch2, patch3, patch4]

        patch5 = ('add', 'foo', [(0, 'Bob')])
        patch6 = ('add', 'foo', [(1, 'Jo')])
        patch7 = ('add', 'foo', [(2, 'Jack')])
        patch8 = ('add', 'foo', [(3, 'John')])

        patches2 = [patch5, patch6, patch7, patch8]

        # Default wrap
        wrapping = [{'patches': [('add', 'authors', [(0, 'Bob')])],
                     'path': ('authors', OrderedSet([0]))},
                    {'patches': [('add', 'authors', [(1, 'Jo')])],
                     'path': ('authors', OrderedSet([1]))},
                    {'patches': [('add', 'authors', [(2, 'Jack')])],
                     'path': ('authors', OrderedSet([2]))},
                    {'patches': [('add', 'authors', [(3, 'John')])],
                     'path': ('authors', OrderedSet([3]))}]

        self.assertEqual(patches1, list(unwrap(wrapping)))

        # SequenceWrapper
        wrapping = [{'patches': [('add', 'authors', [(0, 'Bob')]),
                                 ('add', 'authors', [(1, 'Jo')]),
                                 ('add', 'authors', [(2, 'Jack')]),
                                 ('add', 'authors', [(3, 'John')])],
                     'path': ('authors', OrderedSet([0, 1, 2, 3]))}]

        self.assertEqual(patches1, list(unwrap(wrapping)))

        # Mixed
        wrapping = [{'patches': [('add', 'authors', [(0, 'Bob')]),
                                 ('add', 'authors', [(1, 'Jo')]),
                                 ('add', 'authors', [(2, 'Jack')]),
                                 ('add', 'authors', [(3, 'John')])],
                     'path': ('authors', OrderedSet([0, 1, 2, 3]))},
                    {'patches': [('add', 'foo', [(0, 'Bob')])],
                     'path': ('foo', OrderedSet([0]))},
                    {'patches': [('add', 'foo', [(1, 'Jo')])],
                     'path': ('foo', OrderedSet([1]))},
                    {'patches': [('add', 'foo', [(2, 'Jack')])],
                     'path': ('foo', OrderedSet([2]))},
                    {'patches': [('add', 'foo', [(3, 'John')])],
                     'path': ('foo', OrderedSet([3]))}]

        self.assertEqual(patches1+patches2, list(unwrap(wrapping)))


from dictdiffer.wrappers import (BaseWrapper,
                                 DefaultWrapper,
                                 SequenceWrapper)


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
        self.assertEqual({'path': (OrderedSet(['author']),),
                          'patches': [patch]}, dw.wrap(patch, patches))

        patch = ('add/delete', 'authors', [('name', 'Bob')])
        patches = [patch, patch, patch]
        self.assertEqual({'path': ('authors', OrderedSet(['name'])),
                          'patches': [patch]}, dw.wrap(patch, patches))


class SequenceWrapperTest(unittest.TestCase):
    def test_sequence_wrapper(self):
        sw = SequenceWrapper()

        # Check initialization
        self.assertEqual([], sw._checked_patches)

        # Check already checked patches
        sw._checked_patches.append(('author',))
        patch = ('add/delete', '', [('author', 'Bob')])
        self.assertEqual(None, sw.wrap(patch, None))

        sw._checked_patches.append(('authors', 'name'))
        patch = ('add/delete', 'authors', [('name', 'Bob')])
        self.assertEqual(None, sw.wrap(patch, None))

        # The rest
        sw._checked_patches = []

        patch1 = ('add', 'authors', [(0, 'Bob')])
        patch2 = ('add', 'authors', [(1, 'Jo')])
        patch3 = ('add', 'authors', [(2, 'Jack')])
        patch4 = ('add', 'authors', [(3, 'John')])

        patches = [patch1, patch2, patch3, patch4]

        self.assertEqual({'path': ('authors', OrderedSet([0, 1, 2, 3])),
                          'patches': [patch1, patch2, patch3, patch4]},
                         sw.wrap(patch1, patches))

        # Test a gap
        sw._checked_patches = []

        patch1 = ('add', 'authors', [(0, 'Bob')])
        patch2 = ('add', 'authors', [(1, 'Jo')])
        patch3 = ('add', 'authors', [(3, 'Jack')])
        patch4 = ('add', 'authors', [(4, 'John')])

        patches = [patch1, patch2, patch3, patch4]

        self.assertEqual({'path': ('authors', OrderedSet([0, 1])),
                          'patches': [patch1, patch2]},
                         sw.wrap(patch1, patches))
        self.assertEqual({'path': ('authors', OrderedSet([3, 4])),
                          'patches': [patch3, patch4]},
                         sw.wrap(patch3, patches))
