# This file is part of Dictdiffer.
#
# Copyright (C) 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utils gathers helper functions, classes for the dictdiffer module."""

from ._compat import string_types


class PathLimit(object):

    """Class to limit recursion depth during the dictdiffer.diff execution."""

    def __init__(self, path_limits=[], final_key=None):
        """Initialize a dictionary structure to determine a path limit.

        :param path_limits: list of keys (tuples) determining the path limits
        :param final_key: the key used in the dictionary to determin if the
                          path is final

            >>> pl = PathLimit( [('foo', 'bar')] , final_key='!@#$%FINAL')
            >>> pl.dict
            {'foo': {'bar': {'!@#$%FINAL': True}}}
        """
        self.final_key = final_key if final_key else '!@#$FINAL'
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
        """Querie the PathLimit object if the given key_path is a limit.

        >>> pl = PathLimit( [('foo', 'bar')] , final_key='!@#$%FINAL')
        >>> pl.path_is_limit( ('foo', 'bar') )
        True
        """
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
