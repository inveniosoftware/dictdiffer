# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

from itertools import starmap, izip_longest


def _find_conflicting_path(patch1, patch2):
    p1p = patch1['path'][:-1] + (patch1['path'][-1][0],)
    p2p = patch2['path'][:-1] + (patch2['path'][-1][0],)

    # This returns the shortest path
    return p1p if len(p1p) <= len(p2p) else p2p


def _auto_resolve(patch1, patch2):
    if any(starmap(lambda x, y: x != y, izip_longest(patch1['patches'],
                                                     patch2['patches']))):
        return False
    patch1['take'] = range(len(patch1['patches']))
    patch2['take'] = [None for _ in range(len(patch1['patches']))]

    return True


def resolve(patches1, patches2, conflicts, actions,
            additional_info=None,
            auto_resolve=_auto_resolve,
            conflicting_path_method=_find_conflicting_path):

    def consecutive_slices(iterable):
        return (iterable[:i] for i in reversed(range(1, len(iterable)+1)))

    unresolved_conflicts = []
    for patch1, patch2 in conflicts:
        conflict_path = conflicting_path_method(patch1, patch2)

        if auto_resolve and auto_resolve(patch1, patch2):
            continue
        # Let's do some cascading here
        for sub_path in consecutive_slices(conflict_path):
            try:
                if actions[sub_path](patch1, patch2, patches1, patches2,
                                     additional_info):
                    break
            except KeyError:
                pass
        else:
            # The conflict could not be resolved
            unresolved_conflicts.append((patch1, patch2))

    return unresolved_conflicts
