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
    """Class wrapping patches coming from dictdiffer.diff, trying to preserve
    information about grouping and the original path."""

    def __init__(self, patches, path):
        """
        :param patches: the patches that are wrapped in the object
        :param path: the path corresponding to the wrapped patches
        """

        self.patches = patches
        self.path = path
        self._calculate_shift_value()

    def _calculate_shift_value(self):
        """Calculates the shift value, by which patches from the other source
        need to be moved if the patches in this PatchWrap are applied."""

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
    """Base class of the wrapper class, providing general functionality."""

    def get_path(self, patch):
        """Extracts and return the path form a dictdiffer.diff patch."""
        return get_path(patch)


class DefaultWrapper(BaseWrapper):
    """This class is responsible of wrapping all those patches, that do not
    need to conserve information about semantic group of patches.

    It corresponds to the classes DictExtractor, ListExctractor and
    SetExtractor.
    """

    def wrap(self, patch, diff_result):
        """Returns a list of PatchWrap objects, wrapping the given 
        *diff_result* accordingly."""

        path = self.get_path(patch)
        path = path[:-1] + (OrderedSet([path[-1]]),)
        return PatchWrap([patch], path)

    def is_applicable(self, _object):
        """Checks if the given data structure is applicable for the 
        DefaultWrapper.wrap method."""

        return True


class SequenceWrapper(BaseWrapper):
    """Wrapper class corresponding to the SequenceExtractor class."""

    def __init__(self):
        """Initializes attributes necessary of finding semantic groups and
        restoring the original path of the patches."""

        self._checked_patches = []
        self.additions = 0
        self.deletions = 0
        self.current_superpath = None

    def _handle_additions(self, patch, diff_result, latest_index, patches, os):
        """Method responsible of handling a sequence of addition patches."""

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
        """Method responsible of handling a sequence of deletion patches."""

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
        """Utility method that foreshadows the *diff_result* parameter to
        distinguish if a changes sequences is followed by a deletion sequence,
        and if those sequences belong together."""

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
        """Method responsible of handling a sequence of additon patches.
        As contrasted with the _handle_addition and _handle_deletion, the
        _handle_changes method needs to handle changes patches followed by
        additions or deletions. It will therefore call the corresponding
        methods if necessary."""

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
        """Returns a list of PatchWrap objects, wrapping the given 
        *diff_result* accordingly."""

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
        """Checks if the given data structure is applicable for the 
        DefaultWrapper.wrap method."""

        return isinstance(_object, list)


EXTRACTOR_WRAPPER_MAP = {DictExtractor: DefaultWrapper,
                         ListExtractor: DefaultWrapper,
                         SetExtractor: DefaultWrapper,
                         SequenceExtractor: SequenceWrapper}


class Wrapper(object):
    """The Wrapper class manages the given <NAME>Wrapper classes and the 
    wrapping process in general."""

    def __init__(self, try_default=True):
        """Initializes the default wrappers."""

        self.wrappers = {dict: DefaultWrapper(),
                         list: DefaultWrapper(),
                         set: DefaultWrapper(),
                         'default': [DefaultWrapper(),
                                     DefaultWrapper(),
                                     DefaultWrapper()]}

        self.try_default = try_default

    def wrap(self, patches, _source1, _source2):
        """The wrap method iterates over the given patches, and decides, based
        on the position in the two sources, and the type of the data structure
        at this given position, which <NAME>Wrapper class to use.

        :param patches: a list of patches extracted form dictdiffer.diff
        :param _source1: The original data structure where some of the patches
                         originated from
        :param _source2: The original data structure where some of the patches
                         originated from
        """

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
        """Utility method that provides a connection between the patch 
        extraction process and the wrapping process.

        :param update: a dictionary containing the used extractors
        """

        for key, value in update.iteritems():
            if key == 'default':
                self.wrappers[key] = [EXTRACTOR_WRAPPER_MAP[x]()
                                      for x in value]
            else:
                self.wrappers[key] = EXTRACTOR_WRAPPER_MAP[value]()

    def _reset_wrappers(self):
        """"Utility method to reset the wrappers before each *wrap* call.
        Since the <NAME>Wrapper classes might store information, it becomes
        necessary to reset them before each *wrap* call."""

        for key, value in self.wrappers.iteritems():
            if key == 'default':
                self.wrappers[key] = [type(x)() for x in value]
            else:
                self.wrappers[key] = type(self.wrappers[key])()

    def _get_wrapper(self, _object, _path, _type):
        """Returns the corresponding <NAME>Wrapper object regarding the given
        path, data structure, and type of the data structure at the given path.
        """

        wrapper = (self.wrappers.get(_path) or self.wrappers.get(_type))

        if wrapper is None:
            if self.try_default:
                for wrapper in self.wrappers['default']:
                    if wrapper.is_applicable(_object):
                        break

        return wrapper
