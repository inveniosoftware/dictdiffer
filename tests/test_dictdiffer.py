# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from dictdiffer import diff, patch, revert, swap, dot_lookup


class DictDifferTests(unittest.TestCase):
    def test_addition(self):
        first = {}
        second = {'a': 'b'}
        diffed = next(diff(first, second))
        assert ('add', '', [('a', 'b')]) == diffed

    def test_deletion(self):
        first = {'a': 'b'}
        second = {}
        diffed = next(diff(first, second))
        assert ('remove', '', [('a', 'b')]) == diffed

    def test_change(self):
        first = {'a': 'b'}
        second = {'a': 'c'}
        diffed = next(diff(first, second))
        assert ('change', 'a', ('b', 'c')) == diffed

        first = {'a': None}
        second = {'a': 'c'}
        diffed = next(diff(first, second))
        assert ('change', 'a', (None, 'c')) == diffed

        first = {'a': 'c'}
        second = {'a': None}
        diffed = next(diff(first, second))
        assert ('change', 'a', ('c', None)) == diffed

        first = {'a': 'c'}
        second = {'a': u'c'}
        diffed = list(diff(first, second))
        assert [] == diffed

        first = {'a': 'b'}
        second = {'a': None}
        diffed = next(diff(first, second))
        assert ('change', 'a', ('b', None)) == diffed

    def test_nodes(self):
        first = {'a': {'b': {'c': 'd'}}}
        second = {'a': {'b': {'c': 'd', 'e': 'f'}}}
        diffed = next(diff(first, second))
        assert ('add', 'a.b', [('e', 'f')]) == diffed

    def test_add_list(self):
        first = {'a': []}
        second = {'a': ['b']}
        diffed = next(diff(first, second))
        assert ('add', 'a', [(0, 'b')]) == diffed

    def test_remove_list(self):
        first = {'a': ['b', 'c']}
        second = {'a': []}
        diffed = list(diff(first, second))
        assert [('remove', 'a', [(1, 'c')]),
                ('remove', 'a', [(0, 'b')])] == diffed

    def test_add_set(self):
        first = {'a': set([1, 2, 3])}
        second = {'a': set([0, 1, 2, 3])}
        diffed = next(diff(first, second))
        assert ('add', 'a', [(0, set([0]))]) == diffed

    def test_remove_set(self):
        first = {'a': set([0, 1, 2, 3])}
        second = {'a': set([1, 2, 3])}
        diffed = next(diff(first, second))
        assert ('remove', 'a', [(0, set([0]))]) == diffed

    def test_change_set(self):
        first = {'a': set([0, 1, 2, 3])}
        second = {'a': set([1, 2, 3, 4])}
        diffed = list(diff(first, second))
        assert ('add', 'a', [(0, set([4]))]) in diffed
        assert ('remove', 'a', [(0, set([0]))]) in diffed

    def test_types(self):
        first = {'a': ['a']}
        second = {'a': 'a'}
        diffed = next(diff(first, second))
        assert ('change', 'a', (['a'], 'a')) == diffed

    def test_ignore_key(self):
        first = {'a': 'a', 'b': 'b', 'c': 'c'}
        second = {'a': 'a', 'b': 2, 'c': 3}
        diffed = next(diff(first, second, ignore=['b']))
        assert ('change', 'c', ('c', 3)) == diffed

    def test_ignore_dotted_key(self):
        first = {'a': {'aa': 'A', 'ab': 'B', 'ac': 'C'}}
        second = {'a': {'aa': 1, 'ab': 'B', 'ac': 3}}
        diffed = next(diff(first, second, ignore=['a.aa']))
        assert ('change', 'a.ac', ('C', 3)) == diffed

    def test_ignore_complex_key(self):
        first = {'a': {1: {'a': 'a', 'b': 'b'}}}
        second = {'a': {1: {'a': 1, 'b': 2}}}
        diffed = next(diff(first, second, ignore=[['a', 1, 'a']]))
        assert ('change', ['a', 1, 'b'], ('b', 2)) == diffed

    def test_ignore_missing_keys(self):
        first = {'a': 'a'}
        second = {'a': 'a', 'b': 'b'}
        assert len(list(diff(first, second, ignore=['b']))) == 0
        assert len(list(diff(second, first, ignore=['b']))) == 0

    def test_ignore_missing_complex_keys(self):
        first = {'a': {1: {'a': 'a', 'b': 'b'}}}
        second = {'a': {1: {'a': 1}}}
        diffed = next(diff(first, second, ignore=[['a', 1, 'b']]))
        assert ('change', ['a', 1, 'a'], ('a', 1)) == diffed
        diffed = next(diff(second, first, ignore=[['a', 1, 'b']]))
        assert ('change', ['a', 1, 'a'], (1, 'a')) == diffed

    def test_complex_diff(self):
        """Check regression on issue #4."""
        from decimal import Decimal

        d1 = {
            'id': 1,
            'code': None,
            'type': u'foo',
            'bars': [
                {'id': 6934900},
                {'id': 6934977},
                {'id': 6934992},
                {'id': 6934993},
                {'id': 6935014}],
            'n': 10,
            'date_str': u'2013-07-08 00:00:00',
            'float_here': 0.454545,
            'complex': [{
                'id': 83865,
                'goal': Decimal('2.000000'),
                'state': u'active'}],
            'profile_id': None,
            'state': u'active'
        }

        d2 = {
            'id': u'2',
            'code': None,
            'type': u'foo',
            'bars': [
                {'id': 6934900},
                {'id': 6934977},
                {'id': 6934992},
                {'id': 6934993},
                {'id': 6935014}],
            'n': 10,
            'date_str': u'2013-07-08 00:00:00',
            'float_here': 0.454545,
            'complex': [{
                'id': 83865,
                'goal': Decimal('2.000000'),
                'state': u'active'}],
            'profile_id': None,
            'state': u'active'
        }

        assert len(list(diff(d1, {}))) > 0
        assert d1['id'] == 1
        assert d2['id'] == u'2'
        assert d1 is not d2
        assert d1 != d2
        assert len(list(diff(d1, d2))) > 0

    def test_list_change(self):
        """Produced diffs should not contain empty list instructions (#30)."""
        first = {"a": {"b": [100, 101, 201]}}
        second = {"a": {"b": [100, 101, 202]}}
        result = list(diff(first, second))
        assert len(result) == 1
        assert result == [('change', ['a', 'b', 2], (201, 202))]

    def test_dict_subclasses(self):
        class Foo(dict):
            pass

        first = Foo({2014: [
            dict(month=6, category=None, sum=672.00),
            dict(month=6, category=1, sum=-8954.00),
            dict(month=7, category=None, sum=7475.17),
            dict(month=7, category=1, sum=-11745.00),
            dict(month=8, category=None, sum=-12140.00),
            dict(month=8, category=1, sum=-11812.00),
            dict(month=9, category=None, sum=-31719.41),
            dict(month=9, category=1, sum=-11663.00),
        ]})

        second = Foo({2014: [
            dict(month=6, category=None, sum=672.00),
            dict(month=6, category=1, sum=-8954.00),
            dict(month=7, category=None, sum=7475.17),
            dict(month=7, category=1, sum=-11745.00),
            dict(month=8, category=None, sum=-12141.00),
            dict(month=8, category=1, sum=-11812.00),
            dict(month=9, category=None, sum=-31719.41),
            dict(month=9, category=2, sum=-11663.00),
        ]})

        diffed = next(diff(first, second))
        assert ('change', [2014, 4, 'sum'], (-12140.0, -12141.0)) == diffed


class DiffPatcherTests(unittest.TestCase):
    def test_addition(self):
        first = {}
        second = {'a': 'b'}
        assert second == patch(
            [('add', '', [('a', 'b')])], first)

        first = {'a': {'b': 'c'}}
        second = {'a': {'b': 'c', 'd': 'e'}}
        assert second == patch(
            [('add', 'a', [('d', 'e')])], first)

    def test_changes(self):
        first = {'a': 'b'}
        second = {'a': 'c'}
        assert second == patch(
            [('change', 'a', ('b', 'c'))], first)

        first = {'a': {'b': {'c': 'd'}}}
        second = {'a': {'b': {'c': 'e'}}}
        assert second == patch(
            [('change', 'a.b.c', ('d', 'e'))], first)

    def test_remove(self):
        first = {'a': {'b': 'c'}}
        second = {'a': {}}
        assert second == patch(
            [('remove', 'a', [('b', 'c')])], first)

        first = {'a': 'b'}
        second = {}
        assert second == patch(
            [('remove', '', [('a', 'b')])], first)

    def test_remove_list(self):
        first = {'a': [1, 2, 3]}
        second = {'a': [1, ]}
        assert second == patch(
            [('remove', 'a', [(2, 3), (1, 2), ]), ], first)

    def test_add_list(self):
        first = {'a': [1]}
        second = {'a': [1, 2]}
        assert second == patch(
            [('add', 'a', [(1, 2)])], first)

        first = {'a': {'b': [1]}}
        second = {'a': {'b': [1, 2]}}
        assert second == patch(
            [('add', 'a.b', [(1, 2)])], first)

    def test_change_list(self):
        first = {'a': ['b']}
        second = {'a': ['c']}
        assert second == patch(
            [('change', 'a.0', ('b', 'c'))], first)

        first = {'a': {'b': {'c': ['d']}}}
        second = {'a': {'b': {'c': ['e']}}}
        assert second == patch(
            [('change', 'a.b.c.0', ('d', 'e'))], first)

        first = {'a': {'b': {'c': [{'d': 'e'}]}}}
        second = {'a': {'b': {'c': [{'d': 'f'}]}}}
        assert second == patch(
            [('change', 'a.b.c.0.d', ('e', 'f'))], first)

    def test_remove_set(self):
        first = {'a': set([1, 2, 3])}
        second = {'a': set([1])}
        assert second == patch(
            [('remove', 'a', [(0, set([2, 3]))])], first)

    def test_add_set(self):
        first = {'a': set([1])}
        second = {'a': set([1, 2])}
        assert second == patch(
            [('add', 'a', [(0, set([2]))])], first)

    def test_dict_int_key(self):
        first = {0: 0}
        second = {0: 'a'}
        first_patch = [('change', [0], (0, 'a'))]
        assert second == patch(first_patch, first)

    def test_dict_combined_key_type(self):
        first = {0: {'1': {2: 3}}}
        second = {0: {'1': {2: '3'}}}
        first_patch = [('change', [0, '1', 2], (3, '3'))]
        assert second == patch(first_patch, first)
        assert first_patch[0] == list(diff(first, second))[0]


class SwapperTests(unittest.TestCase):
    def test_addition(self):
        result = 'add', '', [('a', 'b')]
        swapped = 'remove', '', [('a', 'b')]
        assert next(swap([result])) == swapped

        result = 'remove', 'a.b', [('c', 'd')]
        swapped = 'add', 'a.b', [('c', 'd')]
        assert next(swap([result])) == swapped

    def test_changes(self):
        result = 'change', '', ('a', 'b')
        swapped = 'change', '', ('b', 'a')
        assert next(swap([result])) == swapped

    def test_revert(self):
        first = {'a': [1, 2]}
        second = {'a': []}
        diffed = diff(first, second)
        patched = patch(diffed, first)
        assert patched == second
        diffed = diff(first, second)
        reverted = revert(diffed, second)
        assert reverted == first


class DotLookupTest(unittest.TestCase):
    def test_list_lookup(self):
        source = {0: '0'}
        assert dot_lookup(source, [0]) == '0'

    def test_invalit_lookup_type(self):
        self.assertRaises(TypeError, dot_lookup, {0: '0'}, 0)


if __name__ == "__main__":
    unittest.main()
