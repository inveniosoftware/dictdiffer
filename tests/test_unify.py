# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from orderedset import OrderedSet

from dictdiffer import patch
from dictdiffer.extractors import Extractor, SequenceExtractor
from dictdiffer.merger import Merger
from dictdiffer.unify import Unifier
from dictdiffer.utils import WildcardDict
from dictdiffer.wrappers import PatchWrap


class TestUnifier(unittest.TestCase):
    def test_init(self):
        u = Unifier()
        self.assertEqual(u.unified_patches, [])
        self.assertEqual(u.shift_store, {'f': {}, 's': {}})

    def test_order_path(self):
        u = Unifier()

        # INDEX
        pw = PatchWrap([], (OrderedSet([0, 1, 2]),))
        self.assertEqual(u._order_path(pw), (1.0,))

        pw = PatchWrap([], (OrderedSet([0, 1, 2, 3]),))
        self.assertEqual(u._order_path(pw), (1.5,))

        pw = PatchWrap([], (OrderedSet([1, 2, 3, 4]),))
        self.assertEqual(u._order_path(pw), (2.5,))

        # NO INDEX
        pw = PatchWrap([], (OrderedSet(['foo']),))
        self.assertEqual(u._order_path(pw), ('foo',))

        pw = PatchWrap([], (OrderedSet(['foo', 'bar']),))
        self.assertEqual(u._order_path(pw), ('foo',))

        # LONGER PATH
        pw = PatchWrap([], ('author', OrderedSet([0, 1, 2])))
        self.assertEqual(u._order_path(pw), ('author', 1.0))

        pw = PatchWrap([], ('author', OrderedSet(['foo']),))
        self.assertEqual(u._order_path(pw), ('author', 'foo'))

    def test_unify_list(self):
        def take_first(conflict, _, __, ___):
            conflict.take = [('f', x) for x
                             in range(len(conflict.first_patch.patches))]
            return True

        def take_second(conflict, _, __, ___):
            conflict.take = [('s', x) for x
                             in range(len(conflict.second_patch.patches))]
            return True

        actions1 = WildcardDict({('*',): take_first})
        actions2 = WildcardDict({('*',): take_second})

        # CHANGES
        lca = [1, 2, 3]
        first = [2, 3, 4]
        second = [3, 4, 5]

        m = Merger(lca, first, second, actions1)
        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 3, 4])

        m = Merger(lca, first, second, actions2)
        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [3, 4, 5])

        # ONE CHANGE
        lca = [1, 2, 3]
        first = [1, 2, 3]
        second = [3, 4, 5]

        m = Merger(lca, first, second, actions1)
        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [3, 4, 5])

        # ADDITIONS
        lca = [1, 2, 3]
        first = [2, 3, 4]
        second = [3, 4, 5, 6]

        m = Merger(lca, first, second, actions1)
        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 3, 4, 6])

        lca = [1, 2, 3]
        first = [2, 3, 4]
        second = [1, 2, 3, 6]

        m = Merger(lca, first, second, actions2)
        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 3, 4, 6])

        # DELETIONS
        lca = [1, 2, 3]
        first = [2, 3, 4]
        second = [3, 4]

        m = Merger(lca, first, second, actions1)
        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 3, 4])

        lca = [1, 2, 3]
        first = [2, 3, 4]
        second = [1, 2]

        m = Merger(lca, first, second, actions2)
        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 3])
        lca = [1, 2, 3]
        first = [1, 2]
        second = [2, 3, 4]

        m = Merger(lca, first, second, actions2)
        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 3, 4])

    def test_unify_sequence(self):
        def take_first(conflict, _, __, ___):
            conflict.take = [('f', x) for x
                             in range(len(conflict.first_patch.patches))]
            return True

        def take_second(conflict, _, __, ___):
            conflict.take = [('s', x) for x
                             in range(len(conflict.second_patch.patches))]
            return True

        actions1 = WildcardDict({('*',): take_first})
        actions2 = WildcardDict({('*',): take_second})
        # THIS COMES LAST
        # NO CONFLICT
        # lca =    [   1,    3,    5,    7,    9,    11]
        # first =  [0, 1,    3, 4, 5,    7, 8, 9,    11]
        # second = [   1, 2, 3,    5, 6, 7,    9, 10, 11]

        lca = [1, 3, 5, 7, 9, 11]
        first = [0, 1, 3, 4, 5, 7, 8, 9, 11]
        second = [1, 2, 3, 5, 6, 7, 9, 10, 11]

        m = Merger(lca, first, second, {})
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [0, 1, 2, 3,
                                                               4, 5, 6, 7,
                                                               8, 9, 10, 11])

        # lca =    [               5]
        # first =  [0, 1, 2, 3, 4, 5]
        # second = [               5, 6, 7, 8, 9]

        lca = [5]
        first = [0, 1, 2, 3, 4, 5]
        second = [5, 6, 7, 8, 9]

        m = Merger(lca, first, second, {})
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [0, 1, 2, 3,
                                                               4, 5, 6, 7,
                                                               8, 9])

        # lca =    [               5]
        # first =  [0, 1, 2, 3, 4, 5]
        # second = [               5]

        lca = [5]
        first = [0, 1, 2, 3, 4, 5]
        second = [5]

        m = Merger(lca, first, second, {})
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [0, 1, 2, 3,
                                                               4, 5])

        # CONFLICT
        # lca =    [      1,    3,    5]
        # first =  [0, 0, 1,    3, 4, 5]
        # second = [0,    1, 2, 3,    5]

        lca = [1, 3, 5]
        first = [0, 0, 1, 3, 4, 5]
        second = [0, 1, 2, 3, 5]

        m = Merger(lca, first, second, actions1)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [0, 0, 1, 2,
                                                               3, 4, 5])

        # lca =    [      1,    3,    5]
        # first =  [0, 0, 1,    3, 4, 5]
        # second = [0,    1, 2, 3,    5]

        lca = [1, 3, 5]
        first = [0, 0, 1, 3, 4, 5]
        second = [0, 1, 2, 3, 5]

        m = Merger(lca, first, second, actions2)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [0, 1, 2, 3,
                                                               4, 5])

        # lca =    [      1,    3,    5,       7]
        # first =  [0, 0, 1,    3, 4, 5, 6,    7]
        # second = [0,    1, 2, 3,    5, 6, 6, 7]

        lca = [1, 3, 5, 7]
        first = [0, 0, 1, 3, 4, 5, 6, 7]
        second = [0, 1, 2, 3, 5, 6, 6, 7]

        m = Merger(lca, first, second, actions1)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [0, 0, 1, 2,
                                                               3, 4, 5, 6, 7])

        # lca =    [      1,    3,    5,       7]
        # first =  [0, 0, 1,    3, 4, 5, 6,    7]
        # second = [0,    1, 2, 3,    5, 6, 6, 7]

        lca = [1, 3, 5, 7]
        first = [0, 0, 1, 3, 4, 5, 6, 7]
        second = [0, 1, 2, 3, 5, 6, 6, 7]

        m = Merger(lca, first, second, actions2)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [0, 1, 2, 3, 4,
                                                               5, 6, 6, 7])

        # lca =    [      1,    3,    5,       7,    9,     11]
        # first =  [0, 0, 1,    3, 4, 5, 6,    7, 8, 9,     11]
        # second = [0,    1, 2, 3,    5, 6, 6, 7,    9, 10, 11]

        lca = [1, 3, 5, 7, 9, 11]
        first = [0, 0, 1, 3, 4, 5, 6, 7, 8, 9, 11]
        second = [0, 1, 2, 3, 5, 6, 6, 7, 9, 10, 11]

        m = Merger(lca, first, second, actions1)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [0, 0, 1, 2, 3,
                                                               4, 5, 6, 7, 8,
                                                               9, 10, 11])

        # DELETIONS
        # lca =    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        # first =  [   1,    3,    5,    7,    9]
        # second = [0,    2,    4,    6,    8   ]

        lca = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        first = [1, 3, 5, 7, 9]
        second = [0, 2, 4, 6, 8]

        m = Merger(lca, first, second, {})
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [])

        # lca =    [0, 1, 2, 3, 4, 5            ]
        # first =  [               5            ]
        # second = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        lca = [0, 1, 2, 3, 4, 5]
        first = [5]
        second = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        m = Merger(lca, first, second, {})
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [5, 6, 7, 8, 9])

        # lca =    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        # first =  [      2, 3, 4, 5,    7,    9]
        # second = [   1, 2,    4, 5, 6,    8   ]

        lca = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        first = [2, 3, 4, 5, 7, 9]
        second = [1, 2, 4, 5, 6, 8]

        m = Merger(lca, first, second, actions1)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 4, 5])

        # lca =    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        # first =  [      2, 3, 4, 5,    7,    9]
        # second = [   1, 2,    4, 5, 6,    8   ]

        lca = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        first = [2, 3, 4, 5, 7, 9]
        second = [1, 2, 4, 5, 6, 8]

        m = Merger(lca, first, second, actions2)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [1, 2, 4, 5])

        # ALL

        # lca =    [0, 1, 2, 3, 4,    6,    8]
        # first =  [      2, 3, 4, 5, 6  ,  8]
        # second = [   1, 2,    4,    6, 7, 8]

        lca = [0, 1, 2, 3, 4, 6, 8]
        first = [2, 3, 4, 5, 6, 8]
        second = [1, 2, 4, 6, 7, 8]

        m = Merger(lca, first, second, actions1)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 4, 5, 6,
                                                               7, 8])

        # lca =    [0, 1, 2, 3, 4,    6,    8]
        # first =  [      2, 3, 4, 5, 6  ,  8]
        # second = [   1, 2,    4,    6, 7, 8]

        lca = [0, 1, 2, 3, 4, 6, 8]
        first = [2, 3, 4, 5, 6, 8]
        second = [1, 2, 4, 6, 7, 8]

        m = Merger(lca, first, second, actions2)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [1, 2, 4, 5, 6,
                                                               7, 8])

        # lca =    [0, 1, 2, 3, 4,  5, 6,    8]
        # first =  [      2, 3, 4,  9, 6  ,  8]
        # second = [   1, 2,    4, 10, 6, 7, 8]

        lca = [0, 1, 2, 3, 4, 5, 6, 8]
        first = [2, 3, 4, 9, 6, 8]
        second = [1, 2, 4, 10, 6, 7, 8]

        m = Merger(lca, first, second, actions1)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [2, 4, 9, 6,
                                                               7, 8])

        # lca =    [0, 1, 2, 3, 4,  5, 6,    8]
        # first =  [      2, 3, 4,  9, 6  ,  8]
        # second = [   1, 2,    4, 10, 6, 7, 8]

        lca = [0, 1, 2, 3, 4, 5, 6, 8]
        first = [2, 3, 4, 9, 6, 8]
        second = [1, 2, 4, 10, 6, 7, 8]

        m = Merger(lca, first, second, actions2)
        m.extractor = Extractor({list: SequenceExtractor})
        m.wrapper.update_wrappers(m.extractor.extractors)

        m.run()

        self.assertEqual(list(patch(m.unified_patches, lca)), [1, 2, 4, 10, 6,
                                                               7, 8])

    def test_unify_sequence_random(self):
        import random
        import string
        from itertools import izip_longest

        def random_string(count):
            return ''.join(random.choice(string.ascii_lowercase)
                           for _ in range(count))

        def add_anchor(lca, first, second):
            r = random_string(6)
            for x in [lca, first, second]:
                x.append(r)

        def add_addition(lca, first, second):
            first_count = random.randint(0, 4)
            second_count = random.randint(0, 4)

            for f, s in izip_longest(range(first_count), range(second_count)):
                lca.append(None)
                if f is not None:
                    first.append(random_string(6))
                else:
                    first.append(None)
                if s is not None:
                    second.append(random_string(6))
                else:
                    second.append(None)

        def add_deletion(lca, first, second):
            first_count = random.randint(0, 4)
            second_count = random.randint(0, 4)

            for f, s in izip_longest(range(first_count), range(second_count)):
                r = random_string(6)

                lca.append(r)
                if f is not None:
                    first.append(None)
                else:
                    first.append(r)
                if s is not None:
                    second.append(None)
                else:
                    first.append(r)

        def add_change(lca, first, second):
            first_count = random.randint(0, 4)
            second_count = random.randint(0, 4)

            for f, s in izip_longest(range(first_count), range(second_count)):
                r = random_string(6)

                lca.append(r)
                if f is not None:
                    first.append(random_string(6))
                else:
                    first.append(r)
                if s is not None:
                    second.append(random_string(6))
                else:
                    first.append(r)

        def generate_sequence(count, take_first=True):
            lca = []
            first = []
            second = []

            for _ in range(count):
                choice = random.randint(0, 99)

                last_choice = ''
                if last_choice != 'anchor':
                    choice = 20

                if 0 <= choice < 25:
                    if last_choice == 'anchor':
                        continue
                    last_choice = 'anchor'
                    add_anchor(lca, first, second)
                elif 25 <= choice < 50:
                    if last_choice == 'add':
                        continue
                    last_choice = 'add'
                    add_addition(lca, first, second)
                elif 50 <= choice < 75:
                    if last_choice == 'del':
                        continue
                    last_choice = 'del'
                    add_deletion(lca, first, second)
                else:
                    if last_choice == 'change':
                        continue
                    last_choice = 'change'
                    add_change(lca, first, second)

            _lca = [x for x in lca if x]
            _first = [x for x in first if x]
            _second = [x for x in second if x]

            res = []

            for l, f, s in zip(lca, first, second):
                if l == f == s:
                    res.append(l)
                elif l is None:
                    # This means we have an addition
                    if f is not None and s is not None:
                        if take_first:
                            res.append(f)
                        else:
                            res.append(s)
                    elif f is None:
                        res.append(s)
                    else:
                        res.append(f)
                else:
                    # Deletion or change
                    if take_first:
                        res.append(f)
                    else:
                        res.append(s)

            return _lca, _first, _second, [x for x in res if x]

        def take_first(conflict, _, __, ___):
            conflict.take = [('f', x) for x
                             in range(len(conflict.first_patch.patches))]
            return True

        def take_second(conflict, _, __, ___):
            conflict.take = [('s', x) for x
                             in range(len(conflict.second_patch.patches))]
            return True

        actions1 = WildcardDict({('*',): take_first})
        # RANDOM
        for _ in range(1000):
            lca, first, second, res = generate_sequence(10)

            m = Merger(lca, first, second, actions1)
            m.extractor = Extractor({list: SequenceExtractor})
            m.wrapper.update_wrappers(m.extractor.extractors)

            m.run()
            self.assertEqual(list(patch(m.unified_patches, lca)), res)

    def test_shift_patch(self):
        u = Unifier()
        u.shift_store = {'f': {(): [(1, 1), (3, 1), (7, 1)]},
                         's': {(): []}}

        p = ('add/delete', '', [(0, 'Hello')])
        self.assertEqual(u._shift_patch(p, 'f', 0),
                         ('add/delete', '', [(0, 'Hello')]))

        p = ('add/delete', '', [(2, 'Hello')])
        self.assertEqual(u._shift_patch(p, 'f', 2),
                         ('add/delete', '', [(3, 'Hello')]))

        p = ('add/delete', '', [(5, 'Hello')])
        self.assertEqual(u._shift_patch(p, 'f', 5),
                         ('add/delete', '', [(7, 'Hello')]))

        p = ('add/delete', '', [(8, 'Hello')])
        self.assertEqual(u._shift_patch(p, 'f', 8),
                         ('add/delete', '', [(11, 'Hello')]))

        p = ('add/delete', '', [(0, 'Hello')])
        self.assertEqual(u._shift_patch(p, 's', 0),
                         ('add/delete', '', [(0, 'Hello')]))

    def test_rebuild_patch(self):
        u = Unifier()
        # ADD or DELETE
        p1 = ('add/delete', '', [(0, 'Hello')])
        self.assertEqual(u._rebuild_patch(p1, 1),
                         ('add/delete', '', [(1, 'Hello')]))

        p2 = ('add/delete', 'foo', [(0, 'Hello')])
        self.assertEqual(u._rebuild_patch(p2, 1),
                         ('add/delete', 'foo', [(1, 'Hello')]))

        p3 = ('add/delete', 'foo.bar', [(0, 'Hello')])
        self.assertEqual(u._rebuild_patch(p3, 1),
                         ('add/delete', 'foo.bar', [(1, 'Hello')]))

        p4 = ('add/delete', ['foo'], [(0, 'Hello')])
        self.assertEqual(u._rebuild_patch(p4, 1),
                         ('add/delete', ['foo'], [(1, 'Hello')]))

        p5 = ('add/delete', ['foo', 'bar'], [(0, 'Hello')])
        self.assertEqual(u._rebuild_patch(p5, 1),
                         ('add/delete', ['foo', 'bar'], [(1, 'Hello')]))

        # CHANGE
        p1 = ('change', [0], ('Hallo', 'Hello'))
        self.assertEqual(u._rebuild_patch(p1, 1),
                         ('change', [1], ('Hallo', 'Hello')))

        p2 = ('change', ['foo', 0], ('Hallo', 'Hello'))
        self.assertEqual(u._rebuild_patch(p2, 1),
                         ('change', ['foo', 1], ('Hallo', 'Hello')))

        p3 = ('change', ['foo', 'bar', 0], ('Hallo', 'Hello'))
        self.assertEqual(u._rebuild_patch(p3, 1),
                         ('change', ['foo', 'bar', 1], ('Hallo', 'Hello')))

        # NO LIST
        p1 = ('change', 'foo.bar', ('Hallo', 'Hello'))
        self.assertEqual(u._rebuild_patch(p1, 1),
                         ('change', 'foo.bar', ('Hallo', 'Hello')))
