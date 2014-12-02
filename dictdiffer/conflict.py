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
    """Wrapper class carrying two PatchWrap objects which are assigned to be
    conflicting."""

    def __init__(self, first_patch, second_patch):
        """
        :param first_patch: PatchWrap object
        :param second_patch: PatchWrap object
        """

        self.first_patch = first_patch
        self.second_patch = second_patch
        self.handled = False
        self.take = []

    def take_patches(self):
        """Returns an iterator of triples, providing the origin, last element
        of the path and the corresponding patch.

        Utilizes the *take* parameter to find the corresponding patch.

            >>> c = Conflict(pw1, pw2)
            >>> list(c.take_patches())
            [('f', 0, pw1.patches[0]), ('s', 0, pw2.patches[1])]
        """

        _path = self.get_path()
        for p, i in self.take:
            if p == 'f':
                yield ('f', _path[-1][-1], self.first_patch.patches[i])
            if p == 's':
                yield ('s', _path[-1][-1], self.second_patch.patches[i])

    def get_conflict_shift_value(self):
        """Returns the shift values necessary to unify patches regarding which
        of the patches are taken eventually."""

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
        """Returns the path common to the two conflicting patches."""

        first_patch_super = self.first_patch.path[:-1]
        first_patch_last = self.first_patch.path[-1]
        second_patch_last = self.second_patch.path[-1]
        return first_patch_super + (first_patch_last.union(second_patch_last),)

    def __repr__(self):
        return 'Conflict({0}, {1})'.format(self.first_patch, self.second_patch)


class ConflictFinder(object):
    """Class testing two patch lists for possible conflicts."""

    def _is_conflict(self, patch1, patch2):
        """Actual conflict checking method. The current implementation checks
        for path based conflicts, regarding the differences between the
        different kind of patches.

        There are two special cases except from the case of exact paths:

        Super_path: If one path is the super path of another, and one of the
                    two patches is a deletion patch, the two patches are 
                    considered a conflict.

        Addition patches: Congruent paths are not considered conflicting in
                          case of only one of the patches being an addition
                          patch, since in this case, the addition actually
                          happens before the other amendment.

        :param patch1: PatchWrap object
        :param patch2: PatchWrap object
        """
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
        """Method checking each element in *first_patches* against each element
        in *second_patches* to determine potential conflicts.

        :param first_patches: list of PatchWrap objects
        :param second_patches: list of PatchWrap objects
        """

        self.conflicts = [Conflict(patch1, patch2) for patch1, patch2
                          in itertools.product(first_patches,
                                               second_patches)
                          if self._is_conflict(patch1, patch2,
                                               first_patches,
                                               first_patches)]

        return self.conflicts
