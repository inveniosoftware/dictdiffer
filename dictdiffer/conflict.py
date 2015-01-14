# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

from prettytable import PrettyTable
from itertools import product
from orderedset import OrderedSet

from dictdiffer.utils import is_super_path


def _is_conflict(patch1, patch2):
    path1, path2 = patch1['path'], patch2['path']
    conflict, intersection = False, OrderedSet()

    if len(path1) == len(path2):
        if path1[:-1] == path2[:-1]:
            intersection = patch1['path'][-1].intersection(patch2['path'][-1])
            if intersection != OrderedSet():
                conflict = True
    else:
        if is_super_path(path1, path2) or is_super_path(path2, path1):
            conflict = True

    return conflict, intersection


def _handle_conflict(patch1, patch2, _, _1):
    case, _ = _is_conflict(patch1, patch2)
    if case:
        return (patch1, patch2)


def _get_conflicts(patches1, patches2, conflict_handler):
    # TODO: Improvable?
    for patch1, patch2 in product(patches1, patches2):
        yield conflict_handler(patch1, patch2, patches1, patches2)


def get_conflicts(patches1, patches2, conflict_handler=_handle_conflict):
    return (conflict for conflict
            in _get_conflicts(patches1, patches2, conflict_handler)
            if conflict is not None)


def _get_conflicts_string(conflicts):
    def get_path(patch):
        if patch[1] != '':
            keys = (patch[1].split('.') if isinstance(patch[1], str)
                    else patch[1])
        else:
            keys = []
        keys = keys + [patch[2][0]] if patch[0] != 'change' else keys
        if keys == ['']:
            return ''
        return tuple(keys)

    def get_original(patch):
        if patch[0] == 'add':
            return ''
        elif patch[0] == 'remove':
            return patch[2][1]
        else:
            return patch[2][0]

    pt = PrettyTable(['INDEX',
                      'LEFT PATH',
                      'LEFT ACTION',
                      'LEFT VALUE',
                      'ORIGINAL',
                      'RIGHT VALUE',
                      'RIGHT ACTION',
                      'RIGHT PATH'])

    for i, (patch1, patch2) in enumerate(conflicts):
        path1, path2 = patch1['path'][-1], patch2['path'][-1]
        for index, _patch1, _patch2 in zip(path1.union(path2),
                                           patch1['patches'],
                                           patch2['patches']):
            if _patch1 is None:
                _patch1 = ('', '', ('', ''))
            if _patch2 is None:
                _patch2 = ('', '', ('', ''))

            pt.add_row([i,
                        get_path(_patch1),
                        _patch1[0],
                        _patch1[2][1],
                        get_original(_patch1),
                        _patch2[2][1],
                        _patch2[0],
                        get_path(_patch2)])
        pt.add_row(['', '', '', '', '', '', '', ''])

    return pt.get_string()


def print_conflicts(conflicts):
    print _get_conflicts_string(conflicts)
