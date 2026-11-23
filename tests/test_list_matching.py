# SPDX-License-Identifier: MIT

"""List edits must be descriptive, applicable, and exactly reversible."""

from collections import Counter, UserList
from copy import deepcopy
from itertools import product

import pytest

from dictdiffer import diff, patch, revert, swap
from dictdiffer.utils import PathLimit


@pytest.mark.parametrize('first,second,expected', [
    (['one', 'two', 'three'], ['two', 'three'],
     [('remove', '', [(0, 'one')])]),
    ([1, 2, 4, 5], [1, 2, 3, 4, 5], [('add', '', [(2, 3)])]),
    (['a', 'b', 'c', 'd'], ['a', 'd'],
     [('remove', '', [(2, 'c'), (1, 'b')])]),
    ([1, 1, 2], [1, 2], [('remove', '', [(1, 1)])]),
    ([{'name': 'old'}], [{'name': 'new'}],
     [('change', [0, 'name'], ('old', 'new'))]),
])
def test_aligned_edits(first, second, expected):
    """Report middle edits instead of cascading positional replacements."""
    changes = list(diff(first, second, align_lists=True))
    assert changes == expected
    assert patch(changes, first) == second
    assert revert(changes, second) == first


@pytest.mark.parametrize('expand', [False, True])
@pytest.mark.parametrize('path_limit', [None, PathLimit(), PathLimit([('a', 1)])])
def test_exhaustive_ordered_round_trip(expand, path_limit):
    """Exercise duplicate anchors and interacting edits in both directions."""
    sequences = [list(items) for size in range(4)
                 for items in product('ab', repeat=size)]
    for left, right in product(sequences, repeat=2):
        first, second = {'a': left}, {'a': right}
        changes = list(diff(first, second, align_lists=True,
                            expand=expand, path_limit=path_limit))
        assert patch(changes, first) == second
        assert revert(iter(changes), second) == first
        assert list(swap(swap(changes))) == changes


@pytest.mark.parametrize('expand', [False, True])
@pytest.mark.parametrize('dot_notation', [False, True])
def test_nested_edits_and_path_limits(expand, dot_notation):
    """Create containers before editing children and undo children first."""
    first = {'a.b': [{'v': [1, 3]}, {'keep': True}, {'v': [4, 5]}]}
    second = {'a.b': [{'v': [0]}, {'v': [1, 2, 3]}, {'keep': True},
                      {'v': [4, 6]}, {'new': {'x': [7, 8]}}]}
    original = deepcopy(first)
    changes = list(diff(first, second, align_lists=True, path_limit=PathLimit(),
                        expand=expand, dot_notation=dot_notation))
    assert patch(changes, first) == second
    assert revert(changes, second) == original
    assert first == original


def test_matching_honors_numeric_tolerance_and_ignored_fields():
    """Alignment uses the same comparison policy as nested differences."""
    first = [{'n': 10.0, 'secret': 'old'}, {'n': 20.0}]
    second = [{'n': 0}, {'n': 10.01, 'secret': 'new'}, {'n': 20.0}]
    options = dict(align_lists=True, tolerance=.01, ignore=[(1, 'secret')])
    changes = list(diff(first, second, **options))
    assert changes == [('add', '', [(0, {'n': 0})])]
    patched = patch(changes, first)
    assert list(diff(patched, second, **options)) == []
    assert revert(changes, patched) == first


def test_long_single_insertion_and_mutable_sequence():
    """A common prefix/suffix needs no quadratic alignment table."""
    first = UserList(range(10000))
    second = UserList(range(10000))
    second.insert(5000, 'new')
    changes = list(diff(first, second, align_lists=True))
    assert changes == [('add', '', [(5000, 'new')])]
    assert patch(changes, first) == second
    assert revert(changes, second) == first


@pytest.mark.parametrize('expand', [False, True])
def test_unordered_multiset_round_trip(expand):
    """Retain source order and duplicate counts, with an exact inverse."""
    sequences = [list(items) for size in range(4)
                 for items in product('ab', repeat=size)]
    for first, second in product(sequences, repeat=2):
        changes = list(diff(first, second, ignore_order=True, expand=expand))
        patched = patch(changes, first)
        assert Counter(patched) == Counter(second)
        assert revert(changes, patched) == first
        assert len([v for action, _, items in changes for _, v in items
                    if action == 'remove']) == sum((Counter(first) - Counter(second)).values())


def test_unordered_nested_values_and_precedence():
    """Unhashable nested values, sets and duplicate dictionaries can match."""
    first = [{'a': [1, 2]}, {'b': {3}}, {'a': [1, 2]}]
    second = [{'b': {3}}, {'a': [2, 1]}, {'a': [2, 1]}]
    assert list(diff(first, second, ignore_order=True, align_lists=True)) == []
    assert list(diff(first, second))


def test_unordered_overlapping_tolerances():
    """Reassign an earlier match when a greedy choice would lose a pair."""
    first, second = [1.0, 0.0], [0.0, 2.0]
    assert list(diff(first, second, ignore_order=True, tolerance=0,
                     absolute_tolerance=1)) == []
    assert list(diff([float('nan'), 1], [1, float('nan')], ignore_order=True)) == []


def test_unordered_path_limit_and_addition():
    """Path limits aggregate real changes without reporting mere reordering."""
    first = {'same': [1, 2], 'values': [{'a': 1}, {'a': 1}, {'b': 2}]}
    second = {'same': [2, 1], 'values': [{'b': 2}, {'a': 1}, {'c': [3]}]}
    changes = list(diff(first, second, ignore_order=True,
                        path_limit=PathLimit([('same',)])))
    patched = patch(changes, first)
    assert list(diff(patched, second, ignore_order=True)) == []
    assert revert(changes, patched) == first
    assert all(node != ['same'] for _, node, _ in changes)


def test_unordered_ignore_uses_source_positions():
    """An index-qualified ignore refers to the candidate in the first list."""
    first = [{'x': 1, 'ignored': False}, {'x': 2}]
    second = [{'x': 2}, {'x': 1, 'ignored': True}]
    assert list(diff(first, second, ignore_order=True,
                     ignore=[(0, 'ignored')])) == []


@pytest.mark.parametrize('options', [dict(align_lists=True), dict(ignore_order=True)])
def test_payloads_are_copied(options):
    """Later source mutation cannot alter recorded additions or removals."""
    first = [{'a': [1]}, {'keep': 1}]
    second = [{'keep': 1}, {'b': [2]}]
    changes = list(diff(first, second, **options))
    original_changes = deepcopy(changes)
    first[0]['a'].append(9)
    second[-1]['b'].append(8)
    assert changes == original_changes


def test_swap_dependent_edits_and_default_path_limit_siblings():
    """Inverse operations must undo nesting and expanded insertions in reverse."""
    first, second = {}, {'a': {'b': [1, 2]}}
    changes = list(diff(first, second, path_limit=PathLimit(), expand=True))
    assert revert(changes, second) == first
    assert list(diff({'a': 1, 'b': 2}, {'a': 1, 'b': 3},
                     path_limit=[('a',)])) == [('change', 'b', (2, 3))]


def test_default_list_output_is_unchanged():
    """Existing callers keep positional comparison unless they opt in."""
    assert list(diff([1, 2, 3], [2, 3])) == [
        ('change', [0], (1, 2)), ('change', [1], (2, 3)),
        ('remove', '', [(2, 3)])]
