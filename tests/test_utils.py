# This file is part of Dictdiffer.
#
# Copyright (C) 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from dictdiffer.utils import PathLimit, dot_lookup


class UtilsTest(unittest.TestCase):
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

    def test_dot_lookup(self):
        self.assertEqual(dot_lookup({'a': {'b': 'hello'}}, 'a.b'), 'hello')
        self.assertEqual(dot_lookup({'a': {'b': 'hello'}}, ['a', 'b']),
                         'hello')

        self.assertEqual(dot_lookup({'a': {'b': 'hello'}}, 'a.b', parent=True),
                         {'b': 'hello'})
        self.assertEqual(dot_lookup({'a': {'b': 'hello'}}, ''),
                         {'a': {'b': 'hello'}})
