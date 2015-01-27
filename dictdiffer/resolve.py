# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import itertools


class UnresolvedConflictsException(Exception):
    def __init__(self, unresolved_conflicts):
        self.content = unresolved_conflicts


class Resolver(object):
    def __init__(self, first_patches, second_patches, actions,
                 additional_info=None):
        self.first_patches = first_patches
        self.second_patches = second_patches
        self.actions = actions
        self.additional_info = additional_info

        self.unresolved_conflicts = []

    def _auto_resolve(self, conflict):
        patch1 = conflict.first_patch
        patch2 = conflict.second_patch
        if any(itertools.starmap(lambda x, y: x != y,
                                 itertools.izip_longest(patch1.patches,
                                                        patch2.patches))):
            return False

        conflict.take = [('f', x) for x in range(len(patch1.patches))]

        return True

    def _find_conflicting_path(self, conflict):
        patch1 = conflict.first_patch
        patch2 = conflict.second_patch
        p1p = patch1.path[:-1] + (patch1.path[-1][0],)
        p2p = patch2.path[:-1] + (patch2.path[-1][0],)

        # This returns the shortest path
        return p1p if len(p1p) <= len(p2p) else p2p

    def _consecutive_slices(self, iterable):
        return (iterable[:i] for i in reversed(range(1, len(iterable)+1)))

    def resolve_conflicts(self, conflicts):
        for conflict in conflicts:
            conflict_path = self._find_conflicting_path(conflict)

            if self._auto_resolve(conflict):
                continue
            # Let's do some cascading here
            for sub_path in self._consecutive_slices(conflict_path):
                try:
                    if self.actions[sub_path](conflict,
                                              self.first_patches,
                                              self.second_patches,
                                              self.additional_info):
                        break
                except KeyError:
                    pass
            else:
                # The conflict could not be resolved
                self.unresolved_conflicts.append(conflict)

        if self.unresolved_conflicts:
            raise UnresolvedConflictsException(self.unresolved_conflicts)

    def manual_resolve_conflicts(self, picks):
        if len(picks) != len(self.unresolved_conflicts):
            raise UnresolvedConflictsException(self.unresolved_conflicts)
        for pick, conflict in zip(picks, self.unresolved_conflicts):
            conflict.take = pick

        self.unresolved_conflicts = []
