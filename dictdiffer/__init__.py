# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dictdiffer is a helper module to diff and patch dictionaries."""

import sys
import copy

if sys.version_info[0] == 3:  # pragma: no cover (Python 2/3 specific code)
    string_types = str,
else:  # pragma: no cover (Python 2/3 specific code)
    string_types = basestring,

(ADD, REMOVE, CHANGE) = (
    'add', 'remove', 'change')

from .version import __version__

__all__ = ('diff', 'patch', 'swap', 'revert', 'dot_lookup', '__version__')


class PathLimit(object):
    def __init__(self, path_limits=[]):
        self.final_key = '!@#$%FINAL'
        self.dict = {}
        for key_path in path_limits:
            containing = self.dict
            for key in key_path:
                try:
                    containing = containing[key]
                except KeyError:
                    containing[key] = {}
                    containing = containing[key]

            containing[self.final_key] = True

    def path_is_limit(self, key_path):
        containing = self.dict
        for key in key_path:
            try:
                containing = containing[key]
            except KeyError:
                try:
                    containing = containing['*']
                except KeyError:
                    return False

        return containing.get(self.final_key, False)


class DictExtractor(object):
    def is_applicable(self, first, second):
        return isinstance(first, dict) and isinstance(second, dict)

    def extract(self, first, second, node, dotted_node, ignore):
        # dictionaries are not hashable, we can't use sets
        def check(key):
            """Test if key in current node should be ignored."""
            return ignore is None \
                or (dotted_node + [key] if isinstance(dotted_node, list)
                    else '.'.join(node + [str(key)])) not in ignore

        intersection = [k for k in first if k in second and check(k)]
        addition = [k for k in second if k not in first and check(k)]
        deletion = [k for k in first if k not in second and check(k)]

        return intersection, addition, deletion


class ListExtractor(object):
    def is_applicable(self, first, second):
        return isinstance(first, list) and isinstance(second, list)

    def extract(self, first, second, node, dotted_node, ignore):
        len_first = len(first)
        len_second = len(second)

        intersection = list(range(0, min(len_first, len_second)))
        addition = list(range(min(len_first, len_second), len_second))
        deletion = list(reversed(range(min(len_first, len_second), len_first)))

        return intersection, addition, deletion


class SequenceExtractor(object):
    def is_applicable(self, first, second):
        return isinstance(first, list) and isinstance(second, list)

    def extract(self, first, second, node, dotted_node, ignore):
        from difflib import SequenceMatcher
        sequence = SequenceMatcher(None, first, second)

        intersection = []
        addition = []
        deletion = []

        latest_insert = None
        latest_delete = None

        for _tuple in sequence.get_opcodes():
            if _tuple[0] == 'insert':
                if latest_insert == None:
                    latest_insert = _tuple[1]
                else:
                    latest_insert += _tuple[1]
                for new_path in range(_tuple[3], _tuple[4]):
                    addition.append((latest_insert, new_path))
                    latest_insert += 1
            elif _tuple[0] == 'replace':
                pass
            elif _tuple[0] == 'delete':
                #TODO: This needs a lot of thought :/
                if latest_delete = None:
                    latest_delete = _tuple[2]-1
                else:
                    latest_delete -= _tuple[2]
                for i, _ in enumerate(range(_tuple[1], _tuple[2])):
                    deletion.append((latest_delete-i, None))

        return intersection, addition, deletion


EXTRACTORS = {'default': [DictExtractor(), ListExtractor()]}


def _create_dotted_node(node):
    if all(map(lambda x: isinstance(x, string_types), node)):
        return '.'.join(node)
    else:
        return list(node)


def diff(first, second, node=None, ignore=None, extractors=EXTRACTORS,
         expand=False, path_limit=PathLimit()):
    """Compare two dictionary object, and returns a diff result.

    Return iterator with differences between two dictionaries.

        >>> result = diff({'a':'b'}, {'a':'c'})
        >>> list(result)
        [('change', 'a', ('b', 'c'))]

    :param first: original dictionary or list
    :param second: new dictionary or list
    :param node: key for comparison that can be used in :func:`dot_lookup`
    :param ignore: list of keys that should not be checked

    .. versionchanged:: 0.3
       Added *ignore* parameter.
    """
    node = node or []
    dotted_node = _create_dotted_node(node)

    differ = False

    _extractors = (extractors.get(tuple(node)) or
                   extractors.get(type(first)) or
                   extractors['default'])

    for extractor in _extractors:
        if extractor.is_applicable(first, second):
            differ = True
            intersection, addition, deletion = extractor.extract(first, second,
                                                                 node,
                                                                 dotted_node,
                                                                 ignore)
            break

    if differ:
        # Compare if object is a dictionary.
        #
        # Call again the parent function as recursive if dictionary have child
        # objects.  Yields `add` and `remove` flags.
        for key in intersection:
            # if type is not changed, callees again diff function to compare.
            # otherwise, the change will be handled as `change` flag.
            if expand and path_limit.path_is_limit(node+[key]):
                yield CHANGE, _create_dotted_node(node+[key]), (first[key],
                                                                second[key])
            else:
                recurred = diff(
                    first[key],
                    second[key],
                    node=node + [key],
                    ignore=ignore,
                    expand=expand)

                for diffed in recurred:
                    yield diffed

        if addition:
            if expand:
                for key in addition:
                    if path_limit.path_is_limit(node+[key]):
                        yield ADD, dotted_node, [(key, second[key])]
                    else:
                        for extractor in _extractors:
                            if extractor.is_applicable(second[key],
                                                       second[key]):
                                yield (ADD, dotted_node,
                                       [(key, second[key].__class__())])
                                _additions = diff(second[key].__class__(),
                                                  second[key],
                                                  node=node + [key],
                                                  ignore=ignore,
                                                  expand=expand)
                                for _addition in _additions:
                                    yield _addition

                                break
                        else:
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
        # Compare string and integer types and yield `change` flag.
        if first != second:
            yield CHANGE, dotted_node, (first, second)


def patch(diff_result, destination):
    """Patch the diff result to the old dictionary."""
    destination = copy.deepcopy(destination)

    def add(node, changes):
        for key, value in changes:
            dest = dot_lookup(destination, node)
            if isinstance(dest, list):
                dest.insert(key, value)
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
        for key, _ in changes:
            del dot_lookup(destination, node)[key]

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


def dot_lookup(source, lookup, parent=False):
    """Allow you to reach dictionary items with string or list lookup.

    Recursively find value by lookup key split by '.'.

        >>> dot_lookup({'a': {'b': 'hello'}}, 'a.b')
        'hello'

    If parent argument is True, returns the parent node of matched
    object.

        >>> dot_lookup({'a': {'b': 'hello'}}, 'a.b', parent=True)
        {'b': 'hello'}

    If node is empty value, returns the whole dictionary object.

        >>> dot_lookup({'a': {'b': 'hello'}}, '')
        {'a': {'b': 'hello'}}

    """
    if lookup is None or lookup == '' or lookup == []:
        return source

    value = source
    if isinstance(lookup, string_types):
        keys = lookup.split('.')
    elif isinstance(lookup, list):
        keys = lookup
    else:
        raise TypeError('lookup must be string or list')

    if parent:
        keys = keys[:-1]

    for key in keys:
        if isinstance(value, list):
            key = int(key)
        value = value[key]
    return value
