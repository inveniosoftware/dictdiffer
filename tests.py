import unittest

from dictdiffer import diff, patch


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
        assert ('remove', '', ['a']) == diffed

    def test_change(self):
        first = {'a': 'b'}
        second = {'a': 'c'}
        diffed = next(diff(first, second))
        assert ('change', 'a', 'c') == diffed

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
            [('change', 'a', 'c')], first)

        first = {'a': {'b': {'c': 'd'}}}
        second = {'a': {'b': {'c': 'e'}}}
        assert second == patch(
            [('change', 'a.b.c', 'e')], first)

    def test_remove(self):
        first = {'a': {'b': 'c'}}
        second = {'a': {}}
        assert second == patch(
            [('remove', 'a', ['b'])], first)

        first = {'a': 'b'}
        second = {}
        assert second == patch(
            [('remove', '', ['a'])], first)

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


if __name__ == "__main__":
    unittest.main()