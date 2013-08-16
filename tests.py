from testscenarios.scenarios import generate_scenarios
import unittest
from io import BytesIO

import dictdiffer
from dictdiffernew import DictDiffer

from testscenarios import TestWithScenarios

scenario_dictdiffer = ('old',{'differ':dictdiffer})
scenario_dictdiffernew = ('new',{'differ':DictDiffer()})

class DictDifferTests(TestWithScenarios):
    scenarios = [scenario_dictdiffer,scenario_dictdiffernew]
    def test_addition(self):
        """ Test diff with an additional key """
        first = {}
        second = {'a': 'b'}
        diffed = next(self.differ.diff(first, second))
        assert ('add', '', [('a', 'b')]) == diffed

    def test_deletion(self):
        """ Test diff with a removed key """
        first = {'a': 'b'}
        second = {}
        diffed = next(self.differ.diff(first, second))
        assert ('remove', '', [('a', 'b')]) == diffed

    def test_change(self):
        """ Test diff with a changed key """
        first = {'a': 'b'}
        second = {'a': 'c'}
        diffed = next(self.differ.diff(first, second))
        assert ('change', 'a', ('b', 'c')) == diffed

        first = {'a': None}
        second = {'a': 'c'}
        diffed = next(self.differ.diff(first, second))
        assert ('change', 'a', (None, 'c')) == diffed

        first = {'a': None}
        second = {'a': {'a':2}}
        diffed = next(self.differ.diff(first, second))
        assert ('change', 'a', (None, {'a':2})) == diffed

        first = {'a': {'a':2}}
        second = {'a': None}
        diffed = next(self.differ.diff(first, second))
        assert ('change', 'a', ({'a':2},None)) == diffed


    def test_nodes(self):
        """ Test diff with an additional key in a subdictionary """
        first = {'a': {'b': {'c': 'd'}}}
        second = {'a': {'b': {'c': 'd', 'e': 'f'}}}
        diffed = next(self.differ.diff(first, second))
        assert ('add', 'a.b', [('e', 'f')]) == diffed

    def test_push(self):
        """ Test diff with an additional element """
        first = {'a': []}
        second = {'a': ['b']}
        diffed = next(self.differ.diff(first, second))
        assert ('push', 'a', ['b']) == diffed

    def test_pull(self):
        """ Test diff with a removed element """
        first = {'a': ['b']}
        second = {'a': []}
        diffed = next(self.differ.diff(first, second))
        assert ('pull', 'a', ['b']) == diffed


class DiffPatcherTests(TestWithScenarios):
    scenarios = [scenario_dictdiffer,scenario_dictdiffernew]
    def test_addition(self):
        """ Test patch with an additional key """
        first = {}
        second = {'a': 'b'}
        assert second == self.differ.patch(
            [('add', '', [('a', 'b')])], first)

        first = {'a': {'b': 'c'}}
        second = {'a': {'b': 'c', 'd': 'e'}}
        assert second == self.differ.patch(
            [('add', 'a', [('d', 'e')])], first)

    def test_changes(self):
        """ Test patch with a changed key """
        first = {'a': 'b'}
        second = {'a': 'c'}
        assert second == self.differ.patch(
            [('change', 'a', ('b', 'c'))], first)

        first = {'a': {'b': {'c': 'd'}}}
        second = {'a': {'b': {'c': 'e'}}}
        assert second == self.differ.patch(
            [('change', 'a.b.c', ('d', 'e'))], first)

    def test_remove(self):
        """ Test patch for a removed key """
        first = {'a': {'b': 'c'}}
        second = {'a': {}}
        assert second == self.differ.patch(
            [('remove', 'a', [('b', 'c')])], first)

        first = {'a': 'b'}
        second = {}
        assert second == self.differ.patch(
            [('remove', '', [('a', 'b')])], first)

    def test_pull(self):
        """ Test patch for a removed element """
        first = {'a': [1, 2, 3]}
        second = {'a': [1, 2]}
        assert second == self.differ.patch(
            [('pull', 'a', [3])], first)

    def test_push(self):
        """ Test patch for an additional element """
        first = {'a': [1]}
        second = {'a': [1, 2]}
        assert second == self.differ.patch(
            [('push', 'a', [2])], first)

        first = {'a': {'b': [1]}}
        second = {'a': {'b': [1, 2]}}
        assert second == self.differ.patch(
            [('push', 'a.b', [2])], first)


class SwapperTests(TestWithScenarios):
    scenarios = [scenario_dictdiffer,scenario_dictdiffernew]
    def test_addition(self):
        """ Test swap with an additional key """
        result = 'add', '', [('a', 'b')]
        swapped = 'remove', '', [('a', 'b')]
        assert next(self.differ.swap([result])) == swapped

        result = 'remove', 'a.b', [('c', 'd')]
        swapped = 'add', 'a.b', [('c', 'd')]
        assert next(self.differ.swap([result])) == swapped

    def test_changes(self):
        """ Test swap with a changed key """
        result = 'change', '', ('a', 'b')
        swapped = 'change', '', ('b', 'a')
        assert next(self.differ.swap([result])) == swapped

    def test_lists(self):
        """ Test swapping for list element """
        result = 'pull', '', [1, 2]
        swapped = 'push', '', [1, 2]
        assert next(self.differ.swap([result])) == swapped

        result = 'push', '', [1, 2]
        swapped = 'pull', '', [1, 2]
        assert next(self.differ.swap([result])) == swapped

    def test_revert(self):
        """ Tests revert """
        first = {'a': 'b'}
        second = {'a': 'c'}
        diffed = self.differ.diff(first, second)
        patched = self.differ.patch(diffed, first)
        assert patched == second
        diffed = self.differ.diff(first, second)
        reverted = self.differ.revert(diffed, second)
        assert reverted == first

if __name__ == '__main__':
    unittest.main()

