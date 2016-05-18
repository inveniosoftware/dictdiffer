# This file is part of Dictdiffer.
#
# Copyright (C) 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from dictdiffer.utils import (PathLimit, WildcardDict, create_dotted_node,
                              dot_lookup, get_path, is_super_path, nested_hash)


class UtilsTest(unittest.TestCase):
    def test_wildcarddict(self):
        wd = WildcardDict()

        wd[('authors', '*')] = True

        self.assertRaises(KeyError, wd.__getitem__, ('authors',))
        self.assertTrue(wd[('authors', 1)])
        self.assertTrue(wd[('authors', 1, 'name')])
        self.assertTrue(wd[('authors', 1, 'affiliation')])

        del wd[('authors', '*')]

        wd[('authors', '+')] = True

        self.assertRaises(KeyError, wd.__getitem__, ('authors',))
        self.assertTrue(wd[('authors', 1)])
        self.assertRaises(KeyError, wd.__getitem__, ('authors', 1, 'name'))
        self.assertRaises(KeyError, wd.__getitem__, ('authors', 1,
                                                     'affiliation'))

        del wd[('authors', '+')]

        wd[('foo', 'bar')] = True

        self.assertRaises(KeyError, wd.__getitem__, ('foo',))
        self.assertTrue(wd[('foo', 'bar')])
        self.assertRaises(KeyError, wd.__getitem__, ('foo', 'bar', 'banana'))

        # query_path part
        wd = WildcardDict()
        wd[('authors', '*')] = True
        wd[('apple', '+')] = True
        wd[('foo', 'bar')] = True

        self.assertRaises(KeyError, wd.query_path, ('utz',))
        self.assertRaises(KeyError, wd.query_path, ('foo',))
        self.assertRaises(KeyError, wd.query_path, ('bar',))
        self.assertRaises(KeyError, wd.query_path, ('apple', 'banana',
                                                    'mango'))
        self.assertEqual(('authors', '*'), wd.query_path(('authors', 1)))
        self.assertEqual(('authors', '*'), wd.query_path(('authors', 1, 1)))
        self.assertEqual(('authors', '*'), wd.query_path(('authors', 1, 1, 1)))
        self.assertEqual(('apple', '+'), wd.query_path(('apple', 'banana')))
        self.assertEqual(('apple', '+'), wd.query_path(('apple', 'mango')))
        self.assertEqual(('foo', 'bar'), wd.query_path(('foo', 'bar')))

    def test_pathlimit(self):
        path_limit = PathLimit([('author', 'name')])
        self.assertFalse(path_limit.path_is_limit(('author')))
        self.assertTrue(path_limit.path_is_limit(('author', 'name')))
        self.assertFalse(path_limit.path_is_limit(('author', 'name', 'foo')))

        path_limit = PathLimit([('authors', '*')])
        self.assertFalse(path_limit.path_is_limit(('authors')))
        self.assertTrue(path_limit.path_is_limit(('authors', 'name')))
        self.assertTrue(path_limit.path_is_limit(('authors', 1)))
        self.assertTrue(path_limit.path_is_limit(('authors', 2)))
        self.assertFalse(path_limit.path_is_limit(('authors', 'name', 'foo')))

    def test_create_dotted_node(self):
        node = ('foo', 'bar')
        self.assertEqual('foo.bar', create_dotted_node(node))

        node = ('foo', 1)
        self.assertEqual(['foo', 1], create_dotted_node(node))

        node = ('foo', 1, 'bar')
        self.assertEqual(['foo', 1, 'bar'], create_dotted_node(node))

    def test_get_path(self):
        patch = ('add/delete', '', [('author', 'Bob')])
        self.assertEqual(('author',), get_path(patch))
        patch = ('add/delete', 'authors', [('name', 'Bob')])
        self.assertEqual(('authors', 'name'), get_path(patch))
        patch = ('add/delete', 'foo.bar', [('name', 'Bob')])
        self.assertEqual(('foo', 'bar', 'name'), get_path(patch))
        patch = ('add/delete', ['foo', 1], [('name', 'Bob')])
        self.assertEqual(('foo', 1, 'name'), get_path(patch))

        patch = ('change', 'foo', [('John', 'Bob')])
        self.assertEqual(('foo',), get_path(patch))
        patch = ('change', 'foo.bar', [('John', 'Bob')])
        self.assertEqual(('foo', 'bar'), get_path(patch))
        patch = ('change', ['foo', 'bar'], [('John', 'Bob')])
        self.assertEqual(('foo', 'bar'), get_path(patch))
        patch = ('change', ['foo', 1], [('John', 'Bob')])
        self.assertEqual(('foo', 1), get_path(patch))

    def test_is_super_path(self):
        # # True
        path1 = ('authors', 1, 'name')
        path2 = ('authors', 1, 'name')
        self.assertTrue(is_super_path(path1, path2))

        path1 = ('authors', 1)
        path2 = ('authors', 1, 'name')
        self.assertTrue(is_super_path(path1, path2))

        path1 = ('authors',)
        path2 = ('authors', 1, 'name')
        self.assertTrue(is_super_path(path1, path2))

        # # False
        path1 = ('authors', 1, 'name')
        path2 = ('authors', 1, 'surname')
        self.assertFalse(is_super_path(path1, path2))

        path1 = ('authors', 2)
        path2 = ('authors', 1, 'surname')
        self.assertFalse(is_super_path(path1, path2))

        path1 = ('author',)
        path2 = ('authors', 1, 'surname')
        self.assertFalse(is_super_path(path1, path2))

    def test_dot_lookup(self):
        self.assertEqual(dot_lookup({'a': {'b': 'hello'}}, 'a.b'), 'hello')
        self.assertEqual(dot_lookup({'a': {'b': 'hello'}}, ['a', 'b']),
                         'hello')

        self.assertEqual(dot_lookup({'a': {'b': 'hello'}}, 'a.b', parent=True),
                         {'b': 'hello'})
        self.assertEqual(dot_lookup({'a': {'b': 'hello'}}, ''),
                         {'a': {'b': 'hello'}})

    def test_nested_hash(self):
        # No reasonable way to test this
        nested_hash([1, 2, 3])
        nested_hash((1, 2, 3))
        nested_hash(set([1, 2, 3]))
        nested_hash({'foo': 'bar'})
