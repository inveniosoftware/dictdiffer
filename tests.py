import unittest

from dictdiffer import diff, patch, revert, swap


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

    def test_nodes(self):
        first = {'a': {'b': {'c': 'd'}}}
        second = {'a': {'b': {'c': 'd', 'e': 'f'}}}
        diffed = next(diff(first, second))
        assert ('add', 'a.b', [('e', 'f')]) == diffed

    def test_push(self):
        first = {'a': []}
        second = {'a': ['b']}
        diffed = next(diff(first, second))
        assert ('push', 'a', ['b']) == diffed

    def test_pull(self):
        first = {'a': ['b']}
        second = {'a': []}
        diffed = next(diff(first, second))
        assert ('pull', 'a', ['b']) == diffed


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

    def test_pull(self):
        first = {'a': [1, 2, 3]}
        second = {'a': [1, 2]}
        assert second == patch(
            [('pull', 'a', [3])], first)

    def test_push(self):
        first = {'a': [1]}
        second = {'a': [1, 2]}
        assert second == patch(
            [('push', 'a', [2])], first)

        first = {'a': {'b': [1]}}
        second = {'a': {'b': [1, 2]}}
        assert second == patch(
            [('push', 'a.b', [2])], first)


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

    def test_lists(self):
        result = 'pull', '', [1, 2]
        swapped = 'push', '', [1, 2]
        assert next(swap([result])) == swapped

        result = 'push', '', [1, 2]
        swapped = 'pull', '', [1, 2]
        assert next(swap([result])) == swapped

    def test_revert(self):
        first = {'a': 'b'}
        second = {'a': 'c'}
        diffed = diff(first, second)
        patched = patch(diffed, first)
        assert patched == second
        diffed = diff(first, second)
        reverted = revert(diffed, second)
        assert reverted == first

if __name__ == "__main__":
    unittest.main()