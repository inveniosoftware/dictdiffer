# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import itertools


class UnresolvedConflictsException(Exception):
    """Exception raised in case of conflicts, that can not be resolved using
    the provided actions in the automated merging process."""

    def __init__(self, unresolved_conflicts):
        self.content = unresolved_conflicts


class NoFurtherResolutionException(Exception):
    """Exception raised in case that the automatic conflict resolution process
    should stop trying more general keys."""

    pass


class Resolver(object):
    """Class handling the conflict resolution process by presenting the given
    conflicts to actions, designed to solve them."""

    def __init__(self, first_patches, second_patches, actions,
                 additional_info=None):
        """
        :param first_patches: list of PatchWrap objects
        :param second_patches: list of PatchWrap objects
        :param action: WildcardDict object containing the necessary resolution
                      functions
        :param additional_info: any additional information required by the 
                                actions
        """

        self.first_patches = first_patches
        self.second_patches = second_patches
        self.actions = actions
        self.additional_info = additional_info

        self.unresolved_conflicts = []

    def _auto_resolve(self, conflict):
        """Method trying to auto resolve conflicts in case that the perform the
        same amendment."""

        patch1 = conflict.first_patch
        patch2 = conflict.second_patch
        if any(itertools.starmap(lambda x, y: x != y,
                                 itertools.izip_longest(patch1.patches,
                                                        patch2.patches))):
            return False

        conflict.take = [('f', x) for x in range(len(patch1.patches))]

        return True

    def _find_conflicting_path(self, conflict):
        """Returns the shortest path common to the two conflicting PatchWrap
        objects inside the Conflict object."""

        patch1 = conflict.first_patch
        patch2 = conflict.second_patch
        p1p = patch1.path[:-1] + (patch1.path[-1][0],)
        p2p = patch2.path[:-1] + (patch2.path[-1][0],)

        # This returns the shortest path
        return p1p if len(p1p) <= len(p2p) else p2p

    def _consecutive_slices(self, iterable):
        """Builds a list of consecutive slices of a given path.

        >>> list(_consecutive_slices([1, 2, 3]))
        [[1, 2, 3], [1, 2], [1]]
        """

        return (iterable[:i] for i in reversed(range(1, len(iterable)+1)))

    def resolve_conflicts(self, conflicts):
        """Method to present the given conflicts to the actions.

        The method, will map the conflicts to an actions based on the path of
        the conflict. In case that the resolution attempt is not successful, it
        will strip the last element of the path and try again, until the
        resolution is just not possible.

        :param conflicts: list of Conflict objects
        """

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
                # TODO: 
                except NoFurtherResolutionException:
                    self.unresolved_conflicts.append(conflict)
                    break
                except KeyError:
                    pass
            else:
                # The conflict could not be resolved
                self.unresolved_conflicts.append(conflict)

        if self.unresolved_conflicts:
            raise UnresolvedConflictsException(self.unresolved_conflicts)

    def manual_resolve_conflicts(self, picks):
        """Method to resolve conflicts that could not be resolved in an 
        automatic way. The picks parameter utilized the *take* attribute of the
        Conflict objects.

        :param picks: list of lists of tuples, utilizing the *take* parameter
                      of each Conflict object
        """

        if len(picks) != len(self.unresolved_conflicts):
            raise UnresolvedConflictsException(self.unresolved_conflicts)
        for pick, conflict in zip(picks, self.unresolved_conflicts):
            conflict.take = pick

        self.unresolved_conflicts = []
