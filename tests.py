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
        diffed = next(diff(first, second))
        assert ('remove', 'a', [(1, 'c'), (0, 'b'), ]) == diffed

    def test_types(self):
        first = {'a': ['a']}
        second = {'a': 'a'}
        diffed = next(diff(first, second))
        assert ('change', 'a', (['a'], 'a')) == diffed


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
