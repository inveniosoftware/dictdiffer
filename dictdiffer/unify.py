# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.


def contains(patch, conflicts):
    for i, (patch1, patch2) in enumerate(conflicts):
        if patch == patch1 or patch == patch2:
            return i
    return None


def take_patches(patch1, patch2):
    # We will assume that we don't have to fix the indexes here...
    for i, j in zip(patch1['take'], patch2['take']):
        if i is not None and j is not None:
            raise Exception("Can't take two conflicting patches")
        elif i is not None:
            yield patch1['patches'][i]
        elif j is not None:
            yield patch2['patches'][j]

    patch1['taken'] = patch2['taken'] = True


def unify(patches1, patches2, conflicts):
    for patch in patches1 + patches2:
        if 'taken' in patch:
            continue

        index = contains(patch, conflicts)
        if index is not None:
            for p in take_patches(*conflicts[index]):
                yield p
        else:
            for p in patch['patches']:
                yield p
