# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

# TODO: Well, what happens if we want to wrap all lists in the same way...

from orderedset import OrderedSet

from dictdiffer.utils import WildcardDict, get_path


class BaseWrapper(object):
    def get_path(self, patch):
        if patch[1] != '':
            keys = (patch[1].split('.') if isinstance(patch[1], str)
                    else patch[1])
        else:
            keys = []
        keys = keys + [patch[2][0][0]] if patch[0] != 'change' else keys
        return tuple(keys)


class DefaultWrapper(BaseWrapper):
    def wrap(self, patch, diff_result):
        path = self.get_path(patch)
        path = path[:-1] + (OrderedSet([path[-1]]),)
        return {'path': path, 'patches': [patch]}


class SequenceWrapper(BaseWrapper):
    def __init__(self):
        self._checked_patches = []

    def wrap(self, patch, diff_result):
        path = self.get_path(patch)
        if path in self._checked_patches:
            return

        patches = [patch]
        latest_index = path[-1]
        os = OrderedSet([latest_index])
        current_superpath = self.get_path(patch)[:1]

        for _patch in diff_result[diff_result.index(patch)+1:]:
            _path = self.get_path(_patch)
            if _path[:1] != current_superpath:
                break
            if latest_index == _path[-1] - 1:
                self._checked_patches.append(_path)
                patches.append(_patch)
                latest_index = _path[-1]
                os.add(latest_index)
            else:
                break

        path = path[:-1] + (os,)
        return {'path': path, 'patches': patches}


def _prepare_wrappers(w):
    w = w if w else WildcardDict({('*',): DefaultWrapper()})
    if ('*',) not in w:
        w[('*',)] = DefaultWrapper()
    return w


def _wrap(diff_result, wrappers=None):
    wrappers = _prepare_wrappers(wrappers)

    for patch in diff_result:
        yield wrappers[get_path(patch)].wrap(patch, diff_result)


def wrap(diff_result, wrappers=None):
    return (res for res in _wrap(diff_result, wrappers) if res is not None)


def unwrap(wraps):
    return (patch for wrap in wraps for patch in wrap['patches'])
