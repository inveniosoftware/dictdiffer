# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from dictdiffer.extractors import (Extractor,
                                   DictExtractor,
                                   ListExtractor,
                                   SetExtractor)
from dictdiffer.utils import PathLimit


class ExtractorTest(unittest.TestCase):
    def test_init(self):
        # DEFAUL
        e = Extractor()

        extractors = {dict: DictExtractor,
                      list: ListExtractor,
                      set: SetExtractor,
                      'default': [DictExtractor,
                                  ListExtractor,
                                  SetExtractor]}

        self.assertEqual(e.extractors, extractors)
        self.assertEqual(e.ignore, None)
        self.assertEqual(e.try_default, True)
        self.assertEqual(e.expand, False)
        self.assertEqual(type(e.path_limit), PathLimit)

        # EXTRACTOR UPDATE
        e = Extractor(extractor_update={list: SequenceExtractor})

        extractors = {dict: DictExtractor,
                      list: SequenceExtractor,
                      set: SetExtractor,
                      'default': [DictExtractor,
                                  ListExtractor,
                                  SetExtractor]}

        self.assertEqual(e.extractors, extractors)

    def test_extract(self):
        # This is basically tested by the dictdiffer test suit
        first = []
        second = [1, 2, 3]

        e = Extractor()
        self.assertEqual(e.extract(first, second), [('add', '', [(0, 1)]),
                                                    ('add', '', [(1, 2)]),
                                                    ('add', '', [(2, 3)])])


class DictExtractorTest(unittest.TestCase):
    def test_is_applicable(self):
        class NewDict(dict):
            pass

        self.assertTrue(DictExtractor.is_applicable({}, {}))
        self.assertTrue(DictExtractor.is_applicable(NewDict(), NewDict()))
        self.assertTrue(DictExtractor.is_applicable(NewDict(), {}))

        self.assertFalse(DictExtractor.is_applicable({}, []))
        self.assertFalse(DictExtractor.is_applicable({}, set()))
        self.assertFalse(DictExtractor.is_applicable({}, 'Hello'))
        self.assertFalse(DictExtractor.is_applicable({}, 1))

    def test_extract(self):
        # Additions
        first = {}
        second = {'foo': 'bar'}
        res = list(DictExtractor.extract(first, second, None, None, None))

        self.assertEqual([('insert', 'foo', 'foo', None, 'bar')], res)

        first = {}
        second = {'foo': 'bar', 'apple': 'banana'}
        res = list(DictExtractor.extract(first, second, None, None, None))

        self.assertTrue(('insert', 'foo', 'foo', None, 'bar') in res)
        self.assertTrue(('insert', 'apple', 'apple', None, 'banana') in res)

        # Deletions
        first = {'foo': 'bar'}
        second = {}
        res = list(DictExtractor.extract(first, second, None, None, None))

        self.assertEqual([('delete', 'foo', 'foo', 'bar', None)], res)

        first = {'foo': 'bar', 'apple': 'banana'}
        second = {}
        res = list(DictExtractor.extract(first, second, None, None, None))

        self.assertTrue(('delete', 'foo', 'foo', 'bar', None) in res)
        self.assertTrue(('delete', 'apple', 'apple', 'banana', None) in res)

        # Amendments
        first = {'name': 'John'}
        second = {'name': 'Jack'}
        res = list(DictExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 'name', 'name', 'John', 'Jack')], res)

        first = {'name': 'John', 'foo': 'apple'}
        second = {'name': 'Jack', 'foo': 'banana'}
        res = list(DictExtractor.extract(first, second, None, None, None))

        self.assertTrue(('change', 'foo', 'foo', 'apple', 'banana') in res)
        self.assertTrue(('change', 'name', 'name', 'John', 'Jack') in res)

        # All
        first = {'deleteme': 1, 'changeme': 1}
        second = {'addme': 1, 'changeme': 2}
        res = list(DictExtractor.extract(first, second, None, None, None))

        self.assertTrue(('change', 'changeme', 'changeme', 1, 2) in res)
        self.assertTrue(('insert', 'addme', 'addme', None, 1) in res)
        self.assertTrue(('delete', 'deleteme', 'deleteme', 1, None) in res)


class ListExtractorTest(unittest.TestCase):
    def test_is_applicable(self):
        class NewList(list):
            pass

        self.assertTrue(ListExtractor.is_applicable([], []))
        self.assertTrue(ListExtractor.is_applicable(NewList(), NewList()))
        self.assertTrue(ListExtractor.is_applicable(NewList(), []))

        self.assertFalse(ListExtractor.is_applicable([], {}))
        self.assertFalse(ListExtractor.is_applicable([], set()))
        self.assertFalse(ListExtractor.is_applicable([], 'Hello'))
        self.assertFalse(ListExtractor.is_applicable([], 1))

    def test_extract(self):
        # Additions
        first = []
        second = [1]
        res = list(ListExtractor.extract(first, second, None, None, None))

        self.assertEqual([('insert', 0, 0, None, 1)], res)

        first = []
        second = [1, 2]
        res = list(ListExtractor.extract(first, second, None, None, None))

        self.assertEqual([('insert', 0, 0, None, 1),
                          ('insert', 1, 1, None, 2)], res)

        # Deletions
        first = [1]
        second = []
        res = list(ListExtractor.extract(first, second, None, None, None))

        self.assertEqual([('delete', 0, 0, 1, None)], res)

        first = [1, 2]
        second = []
        res = list(ListExtractor.extract(first, second, None, None, None))

        self.assertEqual([('delete', 1, 1, 2, None),
                          ('delete', 0, 0, 1, None)], res)

        # Amendments
        first = [0]
        second = [1]
        res = list(ListExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 0, 0, 0, 1)], res)

        first = [0, 1]
        second = [1, 2]
        res = list(ListExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 0, 0, 0, 1),
                          ('change', 1, 1, 1, 2)], res)

        # All
        first = [0]
        second = [1, 2]
        res = list(ListExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 0, 0, 0, 1),
                          ('insert', 1, 1, None, 2)], res)

        first = [0, 1]
        second = [1]
        res = list(ListExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 0, 0, 0, 1),
                          ('delete', 1, 1, 1, None)], res)


class SetExtractorTest(unittest.TestCase):
    def test_is_applicable(self):
        class NewSet(set):
            pass

        self.assertTrue(SetExtractor.is_applicable(set(), set()))
        self.assertTrue(SetExtractor.is_applicable(NewSet(), NewSet()))
        self.assertTrue(SetExtractor.is_applicable(NewSet(), set()))

        self.assertFalse(SetExtractor.is_applicable(set(), {}))
        self.assertFalse(SetExtractor.is_applicable(set(), []))
        self.assertFalse(SetExtractor.is_applicable(set(), 'Hello'))
        self.assertFalse(SetExtractor.is_applicable(set(), 1))

    def test_extract(self):
        # Additions
        first = set()
        second = set([1])
        res = list(SetExtractor.extract(first, second, None, None, None))

        self.assertEqual([('insert', None, None, None, {1})], res)

        first = set()
        second = set([1, 2])
        res = list(SetExtractor.extract(first, second, None, None, None))

        self.assertEqual([('insert', None, None, None, {1, 2})], res)

        # Deletions
        first = set([1])
        second = set()
        res = list(SetExtractor.extract(first, second, None, None, None))

        self.assertTrue(('delete', None, None, {1}, None) in res)

        first = set([1, 2])
        second = set()
        res = list(SetExtractor.extract(first, second, None, None, None))

        self.assertTrue(('delete', None, None, {1, 2}, None) in res)

        # All
        first = set([2])
        second = set([1])
        res = list(SetExtractor.extract(first, second, None, None, None))

        self.assertTrue(('insert', None, None, None, {1}) in res)
        self.assertTrue(('delete', None, None, {2}, None) in res)


from dictdiffer.extractors import SequenceExtractor


class SequenceExtractorTest(unittest.TestCase):
    def test_is_applicable(self):
        class NewList(list):
            pass

        self.assertTrue(SequenceExtractor.is_applicable([], []))
        self.assertTrue(SequenceExtractor.is_applicable(NewList(), NewList()))
        self.assertTrue(SequenceExtractor.is_applicable(NewList(), []))

        self.assertFalse(SequenceExtractor.is_applicable([], {}))
        self.assertFalse(SequenceExtractor.is_applicable([], set()))
        self.assertFalse(SequenceExtractor.is_applicable([], 'Hello'))
        self.assertFalse(SequenceExtractor.is_applicable([], 1))

    def test_extract(self):
        # This needs more functional testing. Basically just extracting patches
        # from random lists and appplying them to see if the lists turn out
        # the same

        # Additions
        first = []
        second = [1]
        res = list(SequenceExtractor.extract(first, second, None, None, None))

        self.assertEqual([('insert', 0, 0, None, 1)], res)

        first = []
        second = [1, 2]
        res = list(SequenceExtractor.extract(first, second, None, None, None))

        self.assertEqual([('insert', 0, 0, None, 1),
                          ('insert', 1, 1, None, 2)], res)

        # Deletions
        first = [1]
        second = []
        res = list(SequenceExtractor.extract(first, second, None, None, None))

        self.assertEqual([('delete', 0, 0, 1, None)], res)

        first = [1, 2]
        second = []
        res = list(SequenceExtractor.extract(first, second, None, None, None))

        self.assertEqual([('delete', 1, 1, 2, None),
                          ('delete', 0, 0, 1, None)], res)

        # Amendments
        first = [0]
        second = [1]
        res = list(SequenceExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 0, 0, 0, 1)], res)

        first = [0, 1]
        second = [2, 3]
        res = list(SequenceExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 0, 0, 0, 2),
                          ('change', 1, 1, 1, 3)], res)

        # All
        first = [0]
        second = [1, 2]
        res = list(SequenceExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 0, 0, 0, 1),
                          ('insert', 1, 1, None, 2)], res)

        first = [0, 1]
        second = [2]
        res = list(SequenceExtractor.extract(first, second, None, None, None))

        self.assertEqual([('change', 0, 0, 0, 2),
                          ('delete', 1, 1, 1, None)], res)
