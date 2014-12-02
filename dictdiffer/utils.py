# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

from itertools import izip_longest

from orderedset import OrderedSet

from _compat import string_types


class WildcardDict(dict):
    '''
    *:  wildcard for everything that follows
    +:  wildcard for anything on the same path level
    '''
    def __init__(self, values=None):
        super(WildcardDict, self).__init__()
        self.star_keys = set()
        self.plus_keys = set()

        if values is not None:
            for key, value in values.iteritems():
                self.__setitem__(key, value)

    def __getitem__(self, key):
        try:
            return super(WildcardDict, self).__getitem__(key)
        except KeyError:
            if key[:-1] in self.plus_keys:
                return super(WildcardDict, self).__getitem__(key[:-1]+('+',))
            for _key in [key[:-i] for i in range(1, len(key)+1)]:
                if _key in self.star_keys:
                    return super(WildcardDict, self).__getitem__(_key+('*',))
            raise KeyError

    def __setitem__(self, key, value):
        super(WildcardDict, self).__setitem__(key, value)

        if key[-1] == '+':
            self.plus_keys.add(key[:-1])
        if key[-1] == '*':
            self.star_keys.add(key[:-1])

    def query_path(self, key):
        if key in self:
            return key
        if key[:-1] in self.plus_keys:
            return key[:-1]+('+',)
        for _key in [key[:-i] for i in range(1, len(key)+1)]:
            if _key in self.star_keys:
                return _key+('*',)

        raise KeyError


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


def create_dotted_node(node):
    if all(map(lambda x: isinstance(x, string_types), node)):
        return '.'.join(node)
    else:
        return list(node)


def get_path(patch):
    if patch[1] != '':
        keys = patch[1].split('.') if isinstance(patch[1], str) else patch[1]
    else:
        keys = []
    keys = keys + [patch[2][0][0]] if patch[0] != 'change' else keys
    return tuple(keys)


def is_super_path(path1, path2):
    def compare(val1, val2):
        if val1 == val2:
            return True
        elif type(val1) == OrderedSet and type(val2) != OrderedSet:
            return val2 in val1
        elif type(val2) == OrderedSet and type(val1) != OrderedSet:
            return val1 in val2
        else:
            return False

    return all(map(lambda x: compare(x[0], x[1]) or x[0] is None,
                   izip_longest(path1, path2)))


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
