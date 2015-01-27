# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

from .utils import get_path


class Unifier(object):
    def __init__(self):
        self.unified_patches = []
        self.shift_store = {'f': {}, 's': {}}

    def unify(self, first_wrapped_patches, second_wrapped_patches, index):
        self.unified_patches = []
        sorted_patches = sorted(first_wrapped_patches + second_wrapped_patches,
                                key=self._order_path)
        for i, patch in enumerate(sorted_patches):
            patch_origin = patch.source
            other_patch = 's' if patch_origin == 'f' else 'f'
            try:
                conflict = index.conflicts[patch.id]
                if conflict.handled:
                    continue
                conflict.handled = True

                _patches = conflict.take_patches()
                _path = conflict.get_path()
                first, second = conflict.get_conflict_shift_value()
                val = (_path[-1][-1], first)
                try:
                    self.shift_store['f'][_path[:-1]].append(val)
                except KeyError:
                    self.shift_store['f'][_path[:-1]] = [val]

                val = (_path[-1][-1], second)
                try:
                    self.shift_store['s'][_path[:-1]].append(val)
                except KeyError:
                    self.shift_store['s'][_path[:-1]] = [val]
            except KeyError:
                _path = patch.path
                _patches = [(patch_origin, _path[-1][-1], p)
                            for p in patch.patches]
                val = (_path[-1][-1], patch.shift_value)
                try:
                    self.shift_store[other_patch][_path[:-1]].append(val)
                except:
                    self.shift_store[patch_origin][_path[:-1]] = []
                    self.shift_store[other_patch][_path[:-1]] = [val]

            for origin, original_index, p in _patches:
                self.unified_patches.append(self._shift_patch(p, origin,
                                                              original_index))

        return self.unified_patches

    def _order_path(self, patch):
        l = float(len(patch.path[-1]))
        try:
            return patch.path[:-1] + (sum(patch.path[-1])/l, )
        except TypeError:
            return patch.path[:-1] + (patch.path[-1][0],)

    def _shift_patch(self, patch, origin, original_index):
        path = get_path(patch)
        for last_index, amount in self.shift_store[origin][path[:-1]]:
            if original_index > last_index:
                patch = self._rebuild_patch(patch, amount)

        return patch

    def _rebuild_patch(self, p, amount):
        try:
            if p[0] == 'change':
                return (p[0],) + (p[1][:-1] + [p[1][-1]+amount],) + (p[2],)
            else:
                return (p[0],) + (p[1],) + ([(p[2][0][0]+amount, p[2][0][1])],)
        except TypeError:
            return p
