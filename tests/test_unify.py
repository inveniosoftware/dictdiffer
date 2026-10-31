# SPDX-FileCopyrightText: 2015 CERN.
# SPDX-FileCopyrightText: 2026 Shahadat Islam Koyel.
# SPDX-License-Identifier: MIT

import unittest

from dictdiffer import patch
from dictdiffer.conflict import Conflict
from dictdiffer.merge import Merger, UnresolvedConflictsException
from dictdiffer.unify import Unifier
from dictdiffer.utils import WildcardDict, nested_hash


class TestUnifier(unittest.TestCase):

    def test_build_index(self):
        u = Unifier()

        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 1)])
        c = Conflict(p1, p2)

        u._build_index([c])

        self.assertEqual(u._index[nested_hash(p1)], c)
        self.assertEqual(u._index[nested_hash(p2)], c)

    def test_unify(self):
        u = Unifier()

        p1 = ('add', 'foo', [(0, 0)])
        p2 = ('add', 'foo', [(0, 1)])
        c = Conflict(p1, p2)
        c.take = 'f'

        u.unify([p1], [p2], [c])

        self.assertEqual(u.unified_patches, [p1])

    def test_identical_resolved_removal_is_applied_once(self):
        removal = ('remove', '', [('gone', {'value': 1})])
        for selection in ('f', 's'):
            with self.subTest(selection=selection):
                conflict = Conflict(removal, removal)
                conflict.take = selection
                unified = Unifier().unify([removal], [removal], [conflict])
                self.assertEqual(unified, [removal])
                self.assertEqual(patch(unified, {'gone': {'value': 1}}), {})

    def test_identical_removal_merges_without_a_second_delete(self):
        merger = Merger({'gone': 1, 'keep': 2}, {'keep': 2}, {'keep': 2}, {})
        try:
            merger.run()
        except UnresolvedConflictsException as exc:
            merger.continue_run(['f'] * len(exc.content))
        self.assertEqual(patch(merger.unified_patches, merger.lca), {'keep': 2})

    def test_unconflicted_repeated_insertions_are_preserved(self):
        insertion = ('add', '', [(0, {'value': 1})])
        unified = Unifier().unify([insertion], [insertion], [])
        self.assertEqual(unified, [insertion, insertion])
        self.assertEqual(patch(unified, []), [{'value': 1}, {'value': 1}])
