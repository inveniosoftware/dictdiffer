# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dictdiffer is a helper module to diff and patch dictionaries."""

import copy

from .utils import (PathLimit,
                    create_dotted_node,
                    dot_lookup,
                    string_types)
from .version import __version__

(ADD, REMOVE, CHANGE) = (
    'add', 'remove', 'change')

__all__ = ('diff', 'patch', 'swap', 'revert', 'merge',
           'dot_lookup', '__version__')


def diff(first, second, node=None, ignore=None,
         extractors=None, try_default=True,
         expand=False, path_limit=None):
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
    extractors = extractors if extractors else get_default_extractors()
    path_limit = path_limit if path_limit else PathLimit()
    node = node or []
    dotted_node = create_dotted_node(node)

    def get_extractor(extractors, first, second, node, try_default):
        extractor = (extractors.get(tuple(node)) or
                     (extractors.get(type(first))
                      if type(first) == type(second)
                      else None))

        if extractor:
            return extractor
        else:
            if try_default:
                for extractor in extractors['default']:
                    if extractor.is_applicable(first, second):
                        return extractor

    extractor = get_extractor(extractors, first, second, node, try_default)

    diffs = (extractor.extract(first, second, node, dotted_node, ignore)
             if extractor else None)

    if diffs is None:
        # Compare string and integer types and yield `change` flag.
        if first != second:
            yield CHANGE, dotted_node, (first, second)
        return

    for action, first_key, second_key, old_val, new_val in diffs:
        if action == 'change':
            if expand and path_limit.path_is_limit(node+[first_key]):
                yield (CHANGE,
                       create_dotted_node(node+[first_key]),
                       (old_val, new_val))
            else:
                recurred = diff(old_val,
                                new_val,
                                node=node + [first_key],
                                ignore=ignore,
                                extractors=extractors,
                                try_default=try_default,
                                expand=expand,
                                path_limit=path_limit)

                for diffed in recurred:
                    yield diffed
        elif action == 'insert':
            if second_key is not None:
                if expand:
                    if path_limit.path_is_limit(node+[second_key]):
                        yield (ADD, dotted_node,
                               [(second_key, new_val)])
                    else:
                        if get_extractor(extractors,
                                         second[second_key],
                                         second[second_key],
                                         node+[second_key], try_default):
                            yield (ADD, dotted_node,
                                   [(second_key,
                                     new_val.__class__())])
                            _additions = diff(new_val.__class__(),
                                              new_val,
                                              node=node + [second_key],
                                              ignore=ignore,
                                              extractors=extractors,
                                              try_default=try_default,
                                              expand=expand,
                                              path_limit=path_limit)
                            for _addition in _additions:
                                yield _addition
                        else:
                            yield (ADD, dotted_node,
                                   [(second_key, new_val)])
                else:
                    yield ADD, dotted_node, [(second_key, new_val)]
            else:
                yield ADD, dotted_node, [(0, new_val)]
        elif action == 'delete':
            if first_key is not None:
                yield REMOVE, dotted_node, [(first_key, old_val)]
            else:
                yield REMOVE, dotted_node, [(0, old_val)]


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

    for action, node, change in reversed(list(diff_result)):
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


from .extractors import get_default_extractors
from .merger import Merger, UnresolvedConflictsException


def merge(lca, first, second):
    m = Merger(lca, first, second)

    try:
        m.run()
    except UnresolvedConflictsException:
        raise UnresolvedConflictsException(m)

    return m.unified_patches


def continue_merge(merger, picks):
    merger.continue_run(picks)
    return merger.unified_patches
