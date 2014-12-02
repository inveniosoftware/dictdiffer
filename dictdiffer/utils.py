# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

from itertools import izip_longest

from orderedset import OrderedSet

from ._compat import string_types


class WildcardDict(dict):
    """A dictionary that provides special wildcard keys:
        *:  wildcard for everything that follows
        +:  wildcard for anything on the same path level
    The intended use case of this are dictionaries, that utilize tuples as
    keys.

        >>> w = WildcardDict({('foo', '*'): '* card',
        ...                   ('banana', '+'): '+ card'})
        >>> w[ ('foo', 'bar', 'baz') ]
        '* card'
        >>> w[ ('banana', 'apple') ]
        '+ card'
    """

    def __init__(self, values=None):
        """
        :param values: a dictionary

            >>> w = WildcardDict({('foo', '*'): '* card',
            ...                   ('banana', '+'): '+ card'})
            >>> w
            {('foo', 'bar', '*'): 'banana'}
        """

        super(WildcardDict, self).__init__()
        self.star_keys = set()
        self.plus_keys = set()

        if values is not None:
            for key, value in values.iteritems():
                self.__setitem__(key, value)

    def __getitem__(self, key):
        """Returns the value corresponding to the key. If the key doesn't exit
        it tries the '+' wildcard and then the '*' wildcard.

            >>> w = WildcardDict({('foo', '*'): '* card',
            ...                   ('banana', '+'): '+ card'})
            >>> w[ ('foo', 'bar') ]
            '* card'
            >>> w[ ('foo', 'bar', 'baz') ]
            '* card'
            >>> w[ ('banana', 'apple') ]
            '+ card'
            >>> w[ ('banana', 'apple', 'mango') ]
            KeyError
        """

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
        """Returns the key (path) that matches the queried key.

            >>> w = WildcardDict({('foo', '*'): 'banana'})
            >>> w.query_path(('foo', 'bar', 'baz'))
            ('foo', '*')
        """

        if key in self:
            return key
        if key[:-1] in self.plus_keys:
            return key[:-1]+('+',)
        for _key in [key[:-i] for i in range(1, len(key)+1)]:
            if _key in self.star_keys:
                return _key+('*',)

        raise KeyError


class PathLimit(object):
    """PathLimit class to limit the extraction depth during the dictdiffer.diff
    execution."""

    def __init__(self, path_limits=[], final_key=None):
        """Initializes a dictionary structure that is utilized to determine
        whether a given path is at the final depth.

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
        """Queries the PathLimit object if the given key_path is a limit.
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


def create_dotted_node(node):
    """Utility function to create the *dotted node* notation for the
    dictdiffer.diff patches.
        
        >>> create_dotted_node( ['foo', 'bar', 'baz'] )
        'foo.bar.baz'
    """

    if all(map(lambda x: isinstance(x, string_types), node)):
        return '.'.join(node)
    else:
        return list(node)


def get_action(patch):
    """Extracts the action for a given dictdiffer.diff patch. In this case, 
    action means the actual amendment.
    
        >>> get_action( ('change', 'foo', ['bar', 'baz']) )
        ['bar', 'baz']

        >>> get_action( ('add', 'foo', [('bar', 'baz')]) )
        ('bar', 'baz')
    """

    if patch[0] != 'change':
        return patch[2]
    else:
        return patch[2][0]


def get_path(patch):
    """Returns the path for a given dictdiffer.diff patch."""

    if patch[1] != '':
        _str = (str, unicode)
        keys = patch[1].split('.') if isinstance(patch[1], _str) else patch[1]
    else:
        keys = []
    keys = keys + [patch[2][0][0]] if patch[0] != 'change' else keys
    return tuple(keys)


def is_super_path(path1, path2):
    """Checks if one path is the super path of the other.
    Super path means, that the n values in tuple are equal to the first n of m
    vales in tuple b.

        >>> is_super_path( ('foo', 'bar'), ('foo', 'bar') )
        True

        >>> is_super_path( ('foo', 'bar'), ('foo', 'bar', 'baz') )
        True

        >>> is_super_path( ('foo', 'bar'), ('foo', 'apple', 'banana') )
        False
    """

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
