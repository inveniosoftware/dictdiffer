import unittest

from dictdiffer import diff


class DictDifferTests(unittest.TestCase):

    def test_addition(self):
        first = {}
        second = {'a': 'b'}
        diffed = next(diff(first, second))
        assert ('add', '', ['a']) == diffed

    def test_deletion(self):
        first = {'a': 'b'}
        second = {}
        diffed = next(diff(first, second))
        assert ('remove', '', ['a']) == diffed

    def test_nodes(self):
        first = {'a': {'b': {'c': 'd'}}}
        second = {'a': {'b': {'c': 'd', 'e': 'f'}}}
        diffed = next(diff(first, second))
        assert ('add', 'a.b', ['e']) == diffed

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

if __name__ == "__main__":
    unittest.main()