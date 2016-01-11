# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dictdiffer is a helper module to diff and patch dictionaries."""

import sys
import copy
try:
    from collections import Mapping
except ImportError:
    from collections.abc import Mapping

from .utils import are_different, EPSILON, dot_lookup, PathLimit
from .version import __version__
from ._compat import string_types, text_type, PY2


(ADD, REMOVE, CHANGE) = (
    'add', 'remove', 'change')

__all__ = ('diff', 'patch', 'swap', 'revert', 'dot_lookup', '__version__')


def diff(first, second, node=None, ignore=None, path_limit=None, expand=False,
         tolerance=EPSILON):
    """Compare two dictionary/list/set objects, and returns a diff result.

    Return iterator with differences between two dictionaries.

        >>> result = diff({'a':'b'}, {'a':'c'})
        >>> list(result)
        [('change', 'a', ('b', 'c'))]

    PathLimit:

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

    Expand:

        ... list(diff({}, {'foo': 'bar', 'apple': 'mango'}))
        [('add', '', [('foo', 'bar'), ('apple', 'mango')])]

        ... list(diff({}, {'foo': 'bar', 'apple': 'mango'}, expand=True))
        [('add', '', [('foo', 'bar')]), ('add', '', [('apple', 'mango')])]

    :param first: original dictionary, list or set
    :param second: new dictionary, list or set
    :param node: key for comparison that can be used in :func:`dot_lookup`
    :param ignore: list of keys that should not be checked
    :param path_limit: List of path limit tuples or dictdiffer.utils.Pathlimit
                       object to limit the diff recursion depth
    :param expand: Expands the patches
    :param tolerance: threshold to consider 2 values identical

    .. versionchanged:: 0.3
       Added *ignore* parameter.

    .. versionchanged:: 0.4
       Arguments ``first`` and ``second`` can now contain a ``set``.

    .. versionchanged:: 0.5
       Added *path_limit* parameter.
       Added *expand* paramter.
       Added *tolerance* parameter.
    """
    if path_limit is not None and not isinstance(path_limit, PathLimit):
        path_limit = PathLimit(path_limit)

    node = node or []
    if all(map(lambda x: isinstance(x, string_types), node)):
        dotted_node = '.'.join(node)
    else:
        dotted_node = list(node)

    differ = False

    if isinstance(first, Mapping) and isinstance(second, Mapping):
        # dictionaries are not hashable, we can't use sets
        def check(key):
            """Test if key in current node should be ignored."""
            if PY2 and isinstance(key, text_type):
                new_key = key.encode('utf-8')
            else:
                new_key = key
            return ignore is None \
                or (node + [key] if isinstance(dotted_node, list)
                    else '.'.join(node + [str(new_key)])) not in ignore

        intersection = [k for k in first if k in second and check(k)]
        addition = [k for k in second if k not in first and check(k)]
        deletion = [k for k in first if k not in second and check(k)]

        differ = True

    elif isinstance(first, list) and isinstance(second, list):
        len_first = len(first)
        len_second = len(second)

        intersection = list(range(0, min(len_first, len_second)))
        addition = list(range(min(len_first, len_second), len_second))
        deletion = list(reversed(range(min(len_first, len_second), len_first)))

        differ = True

    elif isinstance(first, set) and isinstance(second, set):

        intersection = {}
        addition = second - first
        if len(addition):
            yield ADD, dotted_node, [(0, addition)]
        deletion = first - second
        if len(deletion):
            yield REMOVE, dotted_node, [(0, deletion)]

    if differ:
        # Compare if object is a dictionary.
        #
        # Call again the parent function as recursive if dictionary have child
        # objects.  Yields `add` and `remove` flags.
        for key in intersection:
            # if type is not changed, callees again diff function to compare.
            # otherwise, the change will be handled as `change` flag.
            if path_limit and path_limit.path_is_limit(node+[key]):
                yield CHANGE, node+[key], (first[key], second[key])
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
                    if not isinstance(second[key], (set, list, dict)):
                        collect.append((key, second[key]))
                    elif path_limit.path_is_limit(node+[key]):
                        collect.append((key, second[key]))
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
                        yield ADD, dotted_node, [(key, second[key])]
                else:
                    yield ADD, dotted_node, [
                        # for additions, return a list that consist with
                        # two-pair tuples.
                        (key, second[key]) for key in addition]

        if deletion:
            if expand:
                for key in deletion:
                    yield REMOVE, dotted_node, [(key, first[key])]
            else:
                yield REMOVE, dotted_node, [
                    # for deletions, return the list of removed keys
                    # and values.
                    (key, first[key]) for key in deletion]

    else:
        # Compare string and numerical types and yield `change` flag.
        if are_different(first, second, tolerance):
            yield CHANGE, dotted_node, (first, second)


def patch(diff_result, destination):
    """Patch the diff result to the old dictionary."""
    destination = copy.deepcopy(destination)

    def add(node, changes):
        for key, value in changes:
            dest = dot_lookup(destination, node)
            if isinstance(dest, list):
                dest.insert(key, value)
            elif isinstance(dest, set):
                dest |= value
            else:
                dest[key] = value

    def change(node, changes):
        dest = dot_lookup(destination, node, parent=True)
        if isinstance(node, string_types):
            last_node = node.split('.')[-1]
        else:
            last_node = node[-1]
        if isinstance(dest, list):
            last_node = int(last_node)
        _, value = changes
        dest[last_node] = value

    def remove(node, changes):
        for key, value in changes:
            dest = dot_lookup(destination, node)
            if isinstance(dest, set):
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

        >>> swapped = swap([('add', 'a.b.c', ('a', 'b'))])
        >>> next(swapped)
        ('remove', 'a.b.c', ('a', 'b'))

        >>> swapped = swap([('change', 'a.b.c', ('a', 'b'))])
        >>> next(swapped)
        ('change', 'a.b.c', ('b', 'a'))

    """
    def add(node, changes):
        return REMOVE, node, changes

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


def revert(diff_result, destination):
    """Call swap function to revert patched dictionary object.

    Usage example:

        >>> first = {'a': 'b'}
        >>> second = {'a': 'c'}
        >>> revert(diff(first, second), second)
        {'a': 'b'}

    """
    return patch(swap(diff_result), destination)
