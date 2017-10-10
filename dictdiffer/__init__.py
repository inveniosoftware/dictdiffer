# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2013, 2014, 2015, 2016 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dictdiffer is a helper module to diff and patch dictionaries."""

import sys
from copy import deepcopy

import pkg_resources

from ._compat import (PY2, MutableMapping, MutableSequence, MutableSet,
                      string_types, text_type)
from .utils import EPSILON, PathLimit, are_different, dot_lookup
from .version import __version__

(ADD, REMOVE, CHANGE) = (
    'add', 'remove', 'change')

__all__ = ('diff', 'patch', 'swap', 'revert', 'dot_lookup', '__version__')

DICT_TYPES = (MutableMapping, )
LIST_TYPES = (MutableSequence, )
SET_TYPES = (MutableSet, )

try:
    pkg_resources.get_distribution('numpy')
except pkg_resources.DistributionNotFound:  # pragma: no cover
    HAS_NUMPY = False
else:
    HAS_NUMPY = True

    import numpy

    LIST_TYPES += (numpy.ndarray, )


def diff(first, second, node=None, ignore=None, path_limit=None, expand=False,
         tolerance=EPSILON):
    """Compare two dictionary/list/set objects, and returns a diff result.

    Return an iterator with differences between two objects. The diff items
    represent addition/deletion/change and the item value is a *deep copy*
    from the corresponding source or destination objects.

    >>> from dictdiffer import diff
    >>> result = diff({'a': 'b'}, {'a': 'c'})
    >>> list(result)
    [('change', 'a', ('b', 'c'))]

    The keys can be skipped from difference calculation when they are included
    in ``ignore`` argument of type :class:`collections.Container`.

    >>> list(diff({'a': 1, 'b': 2}, {'a': 3, 'b': 4}, ignore=set(['a'])))
    [('change', 'b', (2, 4))]
    >>> class IgnoreCase(set):
    ...     def __contains__(self, key):
    ...         return set.__contains__(self, str(key).lower())
    >>> list(diff({'a': 1, 'b': 2}, {'A': 3, 'b': 4}, ignore=IgnoreCase('a')))
    [('change', 'b', (2, 4))]

    The difference calculation can be limitted to certain path:

    >>> list(diff({}, {'a': {'b': 'c'}}))
    [('add', '', [('a', {'b': 'c'})])]

    >>> from dictdiffer.utils import PathLimit
    >>> list(diff({}, {'a': {'b': 'c'}}, path_limit=PathLimit()))
    [('add', '', [('a', {})]), ('add', 'a', [('b', 'c')])]

    >>> from dictdiffer.utils import PathLimit
    >>> list(diff({}, {'a': {'b': 'c'}}, path_limit=PathLimit([('a',)])))
    [('add', '', [('a', {'b': 'c'})])]

    >>> from dictdiffer.utils import PathLimit
    >>> list(diff({}, {'a': {'b': 'c'}},
    ...           path_limit=PathLimit([('a', 'b')])))
    [('add', '', [('a', {})]), ('add', 'a', [('b', 'c')])]

    The patch can be expanded to small units e.g. when adding multiple values:

    >>> list(diff({'fruits': []}, {'fruits': ['apple', 'mango']}))
    [('add', 'fruits', [(0, 'apple'), (1, 'mango')])]

    >>> list(diff({'fruits': []}, {'fruits': ['apple', 'mango']}, expand=True))
    [('add', 'fruits', [(0, 'apple')]), ('add', 'fruits', [(1, 'mango')])]

    :param first: The original dictionary, ``list`` or ``set``.
    :param second: New dictionary, ``list`` or ``set``.
    :param node: Key for comparison that can be used in :func:`dot_lookup`.
    :param ignore: Set of keys that should not be checked.
    :param path_limit: List of path limit tuples or dictdiffer.utils.Pathlimit
                       object to limit the diff recursion depth.
    :param expand: Expand the patches.
    :param tolerance: Threshold to consider when comparing two float numbers.

    .. versionchanged:: 0.3
       Added *ignore* parameter.

    .. versionchanged:: 0.4
       Arguments ``first`` and ``second`` can now contain a ``set``.

    .. versionchanged:: 0.5
       Added *path_limit* parameter.
       Added *expand* paramter.
       Added *tolerance* parameter.

    .. versionchanged:: 0.7
       Diff items are deep copies from its corresponding objects.
       Argument *ignore* is always converted to a ``set``.
    """
    if path_limit is not None and not isinstance(path_limit, PathLimit):
        path_limit = PathLimit(path_limit)

    if isinstance(ignore, list):
        ignore = {
            tuple(value) if isinstance(value, list) else value
            for value in ignore
        }

    node = node or []

    def dotted(node, default_type=list):
        """Return dotted notation."""
        if all(map(lambda x: isinstance(x, string_types), node)):
            return '.'.join(node)
        else:
            return default_type(node)

    dotted_node = dotted(node)

    differ = False

    if isinstance(first, DICT_TYPES) and isinstance(second, DICT_TYPES):
        # dictionaries are not hashable, we can't use sets
        def check(key):
            """Test if key in current node should be ignored."""
            return ignore is None or (
                dotted(node + [key], default_type=tuple) not in ignore and
                tuple(node + [key]) not in ignore
            )

        intersection = [k for k in first if k in second and check(k)]
        addition = [k for k in second if k not in first and check(k)]
        deletion = [k for k in first if k not in second and check(k)]

        differ = True

    elif isinstance(first, LIST_TYPES) and isinstance(second, LIST_TYPES):
        len_first = len(first)
        len_second = len(second)

        intersection = list(range(0, min(len_first, len_second)))
        addition = list(range(min(len_first, len_second), len_second))
        deletion = list(reversed(range(min(len_first, len_second), len_first)))

        differ = True

    elif isinstance(first, SET_TYPES) and isinstance(second, SET_TYPES):
        # Deep copy is not necessary for hashable items.
        addition = second - first
        if len(addition):
            yield ADD, dotted_node, [(0, addition)]
        deletion = first - second
        if len(deletion):
            yield REMOVE, dotted_node, [(0, deletion)]

    if differ:
        # Compare if object is a dictionary or list.
        #
        # NOTE variables: intersection, addition, deletion contain only
        # hashable types, hence they do not need to be deepcopied.
        #
        # Call again the parent function as recursive if dictionary have child
        # objects.  Yields `add` and `remove` flags.
        for key in intersection:
            # if type is not changed, callees again diff function to compare.
            # otherwise, the change will be handled as `change` flag.
            if path_limit and path_limit.path_is_limit(node+[key]):
                yield CHANGE, node+[key], (
                    deepcopy(first[key]), deepcopy(second[key])
                )
            else:
                recurred = diff(first[key],
                                second[key],
                                node=node + [key],
                                ignore=ignore,
                                path_limit=path_limit,
                                expand=expand,
                                tolerance=tolerance)

                for diffed in recurred:
                    yield diffed

        if addition:
            if path_limit:
                collect = []
                collect_recurred = []
                for key in addition:
                    if not isinstance(second[key],
                                      SET_TYPES + LIST_TYPES + DICT_TYPES):
                        collect.append((key, deepcopy(second[key])))
                    elif path_limit.path_is_limit(node+[key]):
                        collect.append((key, deepcopy(second[key])))
                    else:
                        collect.append((key, second[key].__class__()))
                        recurred = diff(second[key].__class__(),
                                        second[key],
                                        node=node+[key],
                                        ignore=ignore,
                                        path_limit=path_limit,
                                        expand=expand,
                                        tolerance=tolerance)

                        collect_recurred.append(recurred)

                if expand:
                    for key, val in collect:
                        yield ADD, dotted_node, [(key, val)]
                else:
                    yield ADD, dotted_node, collect

                for recurred in collect_recurred:
                    for diffed in recurred:
                        yield diffed
            else:
                if expand:
                    for key in addition:
                        yield ADD, dotted_node, [(key, deepcopy(second[key]))]
                else:
                    yield ADD, dotted_node, [
                        # for additions, return a list that consist with
                        # two-pair tuples.
                        (key, deepcopy(second[key])) for key in addition]

        if deletion:
            if expand:
                for key in deletion:
                    yield REMOVE, dotted_node, [(key, deepcopy(first[key]))]
            else:
                yield REMOVE, dotted_node, [
                    # for deletions, return the list of removed keys
                    # and values.
                    (key, deepcopy(first[key])) for key in deletion]

    else:
        # Compare string and numerical types and yield `change` flag.
        if are_different(first, second, tolerance):
            yield CHANGE, dotted_node, (deepcopy(first), deepcopy(second))


def patch(diff_result, destination, in_place=False):
    """Patch the diff result to the destination dictionary.

    :param diff_result: Changes returned by ``diff``.
    :param destination: Structure to apply the changes to.
    :param in_place: By default, destination dictionary is deep copied
                     before applying the patch, and the copy is returned.
                     Setting ``in_place=True`` means that patch will apply
                     the changes directly to and return the destination
                     structure.
    """
    if not in_place:
        destination = deepcopy(destination)

    def add(node, changes):
        for key, value in changes:
            dest = dot_lookup(destination, node)
            if isinstance(dest, LIST_TYPES):
                dest.insert(key, value)
            elif isinstance(dest, SET_TYPES):
                dest |= value
            else:
                dest[key] = value

    def change(node, changes):
        dest = dot_lookup(destination, node, parent=True)
        if isinstance(node, string_types):
            last_node = node.split('.')[-1]
        else:
            last_node = node[-1]
        if isinstance(dest, LIST_TYPES):
            last_node = int(last_node)
        _, value = changes
        dest[last_node] = value

    def remove(node, changes):
        for key, value in changes:
            dest = dot_lookup(destination, node)
            if isinstance(dest, SET_TYPES):
                dest -= value
            else:
                del dest[key]

    patchers = {
        REMOVE: remove,
        ADD: add,
        CHANGE: change
    }

    for action, node, changes in diff_result:
        patchers[action](node, changes)

    return destination


def swap(diff_result):
    """Swap the diff result.

    It uses following mapping:

    - remove -> add
    - add -> remove

    In addition, swap the changed values for `change` flag.

        >>> from dictdiffer import swap
        >>> swapped = swap([('add', 'a.b.c', [('a', 'b'), ('c', 'd')])])
        >>> next(swapped)
        ('remove', 'a.b.c', [('c', 'd'), ('a', 'b')])

        >>> swapped = swap([('change', 'a.b.c', ('a', 'b'))])
        >>> next(swapped)
        ('change', 'a.b.c', ('b', 'a'))

    """
    def add(node, changes):
        return REMOVE, node, list(reversed(changes))

    def remove(node, changes):
        return ADD, node, changes

    def change(node, changes):
        first, second = changes
        return CHANGE, node, (second, first)

    swappers = {
        REMOVE: remove,
        ADD: add,
        CHANGE: change
    }

    for action, node, change in diff_result:
        yield swappers[action](node, change)


def revert(diff_result, destination, in_place=False):
    """Call swap function to revert patched dictionary object.

    Usage example:

        >>> from dictdiffer import diff, revert
        >>> first = {'a': 'b'}
        >>> second = {'a': 'c'}
        >>> revert(diff(first, second), second)
        {'a': 'b'}

    :param diff_result: Changes returned by ``diff``.
    :param destination: Structure to apply the changes to.
    :param in_place: By default, destination dictionary is deep
                     copied before being reverted, and the copy
                     is returned. Setting ``in_place=True`` means
                     that revert will apply the changes directly to
                     and return the destination structure.
    """
    return patch(swap(diff_result), destination, in_place)
