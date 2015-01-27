# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

from orderedset import OrderedSet

from .utils import get_path, dot_lookup
from .extractors import (DictExtractor, ListExtractor, SetExtractor,
                         SequenceExtractor)


class PatchWrap(object):
    def __init__(self, patches, path):
        self.patches = patches
        self.path = path
        self._calculate_shift_value()

    def _calculate_shift_value(self):
        self.shift_value = 0
        for p in self.patches:
            if p[0] == 'add':
                self.shift_value += 1
            elif p[0] == 'remove':
                self.shift_value -= 1

    def __str__(self):
        return ('PatchWrap({0}, {1})'.format(self.patches, self.path))

    def __repr__(self):
        return ('PatchWrap({0}, {1})'.format(self.patches, self.path))


class BaseWrapper(object):
    def get_path(self, patch):
        return get_path(patch)


class DefaultWrapper(BaseWrapper):
    def wrap(self, patch, diff_result):
        path = self.get_path(patch)
        path = path[:-1] + (OrderedSet([path[-1]]),)
        return PatchWrap([patch], path)

    def is_applicable(self, _object):
        return True


class SequenceWrapper(BaseWrapper):
    def __init__(self):
        self._checked_patches = []
        self.additions = 0
        self.deletions = 0
        self.current_superpath = None

    def _handle_additions(self, patch, diff_result, latest_index, patches, os):
        additions = 0
        for _patch in diff_result[diff_result.index(patch)+1:]:
            _action = _patch[0]
            if _action != 'add':
                break
            _path = self.get_path(_patch)
            if _path[:-1] != self.current_superpath:
                break
            if latest_index == _path[-1] - 1:
                # This means we have a addition
                self._checked_patches.append(_path)
                patches.append(_patch)
                latest_index = _path[-1]
                additions += 1

        return additions

    def _handle_deletions(self, patch, diff_result, latest_index, patches, os):
        deletions = 0
        for _patch in diff_result[diff_result.index(patch)+1:]:
            _action = _patch[0]
            if _action != 'remove':
                break
            _path = self.get_path(_patch)
            if _path[:-1] != self.current_superpath:
                break
            if latest_index == _path[-1] + 1:
                # This means we have a deletion
                deletions += 1
                self._checked_patches.append(_path)
                patches.append(_patch)
                latest_index = _path[-1]
                os.add(latest_index-self.additions+self.deletions)

        return deletions

    def _check_next_removes(self, patch, diff_result, latest_index):
        _latest_index = self.get_path(patch)[-1]
        for _patch in diff_result[diff_result.index(patch)+1:]:
            _action = _patch[0]
            if _action != 'remove':
                break
            _path = self.get_path(_patch)
            if _path[:-1] != self.current_superpath:
                break
            if _latest_index == _path[-1] + 1:
                _latest_index -= 1
            else:
                break

        return _latest_index == latest_index + 1

    def _handle_changes(self, patch, diff_result, latest_index, patches, os):
        last_patch = patch
        additions, deletions = 0, 0
        for _patch in diff_result[diff_result.index(patch)+1:]:
            _path = self.get_path(_patch)
            if _path[:-1] != self.current_superpath:
                break

            _action = _patch[0]
            if _action == 'add':
                previous_len = len(patches)
                additions = self._handle_additions(last_patch, diff_result,
                                                   latest_index,
                                                   patches, os)
                if len(patches) > previous_len:
                    os.add(_path[-1]-self.additions+self.deletions)
                break
            elif _action == 'remove':
                if self._check_next_removes(_patch, diff_result, latest_index):
                    print 'yes'
                    _latest_index = get_path(_patch)[-1]+1
                    deletions = self._handle_deletions(last_patch, diff_result,
                                                       _latest_index,
                                                       patches, os)
                break
            else:
                if latest_index == _path[-1] - 1:
                    # This means we have a deletion
                    self._checked_patches.append(_path)
                    patches.append(_patch)
                    latest_index = _path[-1]
                    os.add(latest_index-self.additions+self.deletions)
                    last_patch = _patch
                else:
                    break

        return additions, deletions

    def wrap(self, patch, diff_result):
        path = self.get_path(patch)
        if path in self._checked_patches:
            return
        # Whatever passes this point is a new start of a wrap

        if path[:-1] != self.current_superpath:
            self.additions = 0
            self.deletions = 0
        self.current_superpath = path[:-1]

        current_action = patch[0]
        patches = [patch]
        latest_index = path[-1]
        os = OrderedSet([latest_index-self.additions+self.deletions])

        if current_action == 'change':
            additions, deletions = self._handle_changes(patch, diff_result,
                                                        latest_index,
                                                        patches, os)
            self.additions += additions
            self.deletions += deletions
        elif current_action == 'add':
            self.additions += 1 + self._handle_additions(patch, diff_result,
                                                         latest_index,
                                                         patches, os)
        else:
            self.deletions += 1 + self._handle_deletions(patch, diff_result,
                                                         latest_index,
                                                         patches, os)

        path = path[:-1] + (os,)
        return PatchWrap(patches, path)

    def is_applicable(self, _object):
        return isinstance(_object, list)


EXTRACTOR_WRAPPER_MAP = {DictExtractor: DefaultWrapper,
                         ListExtractor: DefaultWrapper,
                         SetExtractor: DefaultWrapper,
                         SequenceExtractor: SequenceWrapper}


class Wrapper(object):
    def __init__(self, try_default=True):
        self.wrappers = {dict: DefaultWrapper(),
                         list: DefaultWrapper(),
                         set: DefaultWrapper(),
                         'default': [DefaultWrapper(),
                                     DefaultWrapper(),
                                     DefaultWrapper()]}

        self.try_default = try_default

    def wrap(self, patches, _source1, _source2):
        self._reset_wrappers()

        res = []
        for patch in patches:
            _path = get_path(patch)
            try:
                _object = dot_lookup(_source1, list(_path), parent=True)
            except (KeyError, IndexError):
                _object = dot_lookup(_source2, list(_path), parent=True)
            _type = type(_object)
            wrapped_patch = self._get_wrapper(_object,
                                              _path,
                                              _type).wrap(patch, patches)

            if wrapped_patch:
                res.append(wrapped_patch)

        return res

    def update_wrappers(self, update):
        for key, value in update.iteritems():
            if key == 'default':
                self.wrappers[key] = [EXTRACTOR_WRAPPER_MAP[x]()
                                      for x in value]
            else:
                self.wrappers[key] = EXTRACTOR_WRAPPER_MAP[value]()

    def _reset_wrappers(self):
        for key, value in self.wrappers.iteritems():
            if key == 'default':
                self.wrappers[key] = [type(x)() for x in value]
            else:
                self.wrappers[key] = type(self.wrappers[key])()

    def _get_wrapper(self, _object, _path, _type):
        wrapper = (self.wrappers.get(_path) or self.wrappers.get(_type))

        if wrapper is None:
            if self.try_default:
                for wrapper in self.wrappers['default']:
                    if wrapper.is_applicable(_object):
                        break

        return wrapper
