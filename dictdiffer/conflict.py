# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import itertools

from orderedset import OrderedSet

from .utils import is_super_path


class Conflict(object):
    def __init__(self, first_patch, second_patch):
        self.first_patch = first_patch
        self.second_patch = second_patch
        self.handled = False
        self.take = []

    def take_patches(self):
        _path = self.get_path()
        for p, i in self.take:
            if p == 'f':
                yield ('f', _path[-1][-1], self.first_patch.patches[i])
            if p == 's':
                yield ('s', _path[-1][-1], self.second_patch.patches[i])

    def get_conflict_shift_value(self):
        first_supposed_shifts = self.first_patch.shift_value
        second_supposed_shifts = self.second_patch.shift_value

        res = 0
        for take in self.take:
            p = self.first_patch if take[0] == 'f' else self.second_patch
            p = p.patches[take[1]]

            if p[0] == 'add':
                res += 1
            elif p[0] == 'remove':
                res -= 1

        return res - first_supposed_shifts, res - second_supposed_shifts

    def get_path(self):
        first_patch_super = self.first_patch.path[:-1]
        first_patch_last = self.first_patch.path[-1]
        second_patch_last = self.second_patch.path[-1]
        return first_patch_super + (first_patch_last.union(second_patch_last),)

    def __repr__(self):
        return 'Conflict({0}, {1})'.format(self.first_patch, self.second_patch)


class ConflictFinder(object):
    def _is_conflict(self, patch1, patch2, *args):
        path1, path2 = patch1.path, patch2.path
        conflict, intersection = False, OrderedSet()

        if len(path1) == len(path2):
            if patch1.patches[0][0] == 'add' and patch2.patches[0][0] == 'add':
                if path1[:-1] == path2[:-1]:
                    if path1[-1][0] == path2[-1][0]:
                        conflict = True
            elif (patch1.patches[0][0] == 'add'
                  or patch2.patches[0][0] == 'add'):
                conflict = False
            else:
                if path1[:-1] == path2[:-1]:
                    intersection = path1[-1].intersection(path2[-1])
                    if intersection != OrderedSet():
                        conflict = True
        else:
            if is_super_path(path1, path2) or is_super_path(path2, path1):
                conflict = True

        return conflict

    def find_conflicts(self, first_patches, second_patches):

        self.conflicts = [Conflict(patch1, patch2) for patch1, patch2
                          in itertools.product(first_patches,
                                               second_patches)
                          if self._is_conflict(patch1, patch2,
                                               first_patches,
                                               first_patches)]

        return self.conflicts
