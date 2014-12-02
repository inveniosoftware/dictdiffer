# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

from .extractors import Extractor
from .wrappers import Wrapper
from .conflict import ConflictFinder
from .unify import Unifier
from .resolve import Resolver, UnresolvedConflictsException


class Indexer(object):
    def build_index(self, objects, indexer_name, attribute_seqs):
        self.__setattr__(indexer_name, {})
        index = self.__getattribute__(indexer_name)
        for obj in objects:
            for attribute_seq in attribute_seqs:
                attr = obj
                for attribute_name in attribute_seq:
                    attr = attr.__getattribute__(attribute_name)

                if hasattr(attr, '__iter__'):
                    self._build_list_index(index, attr, obj)
                else:
                    self._build_index(index, attr, obj)

    def _build_list_index(self, index, attr, obj):
        for path in [tuple(attr[:x]) for x in range(len(attr))]:
            _path = path + ('*',)
            try:
                index[_path].append(obj)
            except KeyError:
                index[_path] = [obj]
        for path in [tuple(attr[:-1]) + (x,) for x in attr[-1]]:
            index[path] = [obj]

    def _build_index(self, index, attr, obj):
        index[attr] = obj


class Merger(object):
    def __init__(self, lca, first, second, actions, additional_info=None):
        self.lca = lca
        self.first = first
        self.second = second

        self.actions = actions
        self.additional_info = additional_info

        self.extractor = Extractor()
        self.wrapper = Wrapper()
        self.conflict_finder = ConflictFinder()

        self.unifier = Unifier()

        self.index = Indexer()

        self.conflicts = []
        self.unresolved_conflicts = []

    def run(self):
        self.extract_patches()
        self.wrap_patches()
        self.build_index()
        self.find_conflicts()
        self.build_conflict_index()

        # TODO: Make this like the rest, init first
        self.resolver = Resolver(self.first_wrapped_patches,
                                 self.second_wrapped_patches,
                                 self.actions,
                                 self.additional_info)
        self.resolve_conflicts()

        if self.unresolved_conflicts:
            raise UnresolvedConflictsException(self.unresolved_conflicts)

        self.unify_patches()

    def continue_run(self, picks):
        self.resolver.manual_resolve_conflicts(picks)
        self.unresolved_conflicts = []
        self.unify_patches()

    def extract_patches(self):
        self.first_patches = self.extractor.extract(self.lca, self.first)
        self.second_patches = self.extractor.extract(self.lca, self.second)

    def wrap_patches(self):
        self.first_wrapped_patches = self.wrapper.wrap(self.first_patches,
                                                       self.lca, self.first)
        self.second_wrapped_patches = self.wrapper.wrap(self.second_patches,
                                                        self.lca, self.second)

        id = 0
        for p in self.first_wrapped_patches:
            p.source = 'f'
            p.id = id
            id += 1
        for p in self.second_wrapped_patches:
            p.source = 's'
            p.id = id
            id += 1

    def build_index(self):
        self.index.build_index(self.first_wrapped_patches,
                               'first', [['path']])
        self.index.build_index(self.second_wrapped_patches,
                               'second', [['path']])

    def find_conflicts(self, conflict_handler=None):
        self.conflicts = (self
                          .conflict_finder
                          .find_conflicts(self.first_wrapped_patches,
                                          self.second_wrapped_patches))

    def build_conflict_index(self):
        self.index.build_index(self.conflicts,
                               'conflicts',
                               [['first_patch', 'id'], ['second_patch', 'id']])

    def resolve_conflicts(self):
        try:
            self.resolver.resolve_conflicts(self.conflicts)
        except UnresolvedConflictsException as e:
            self.unresolved_conflicts = e.content

    def unify_patches(self):
        self.unified_patches = self.unifier.unify(self.first_wrapped_patches,
                                                  self.second_wrapped_patches,
                                                  self.index)
