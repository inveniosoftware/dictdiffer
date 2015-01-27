# This file is part of Dictdiffer.
#
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest
import string

from random import randint, choice
from dictdiffer import diff, patch, revert


def generate_random_string(length):
    return ''.join([choice(string.ascii_letters) for _ in range(length)])


def generate_random_dictionary(iterations):
    d = {}
    random_key = generate_random_string(randint(1, 10))
    random_value = generate_random_string(randint(1, 10))
    d[random_key] = {random_key: random_value}

    parent = []
    current = d
    for _ in range(iterations):
        option = randint(0, 100)
        if 0 <= option < 40:
            # Add key
            random_key = generate_random_string(randint(1, 10))
            random_value = generate_random_string(randint(1, 10))
            current[random_key] = {random_key: random_value}
        elif 40 <= option < 80:
            # Go to key
            key = choice(current.keys())
            if type(current[key]) == dict:
                parent.append(current)
                current = current[key]
            else:
                random_key = generate_random_string(randint(1, 10))
                random_value = generate_random_string(randint(1, 10))
                current[random_key] = {random_key: random_value}
        elif 80 <= option <= 100:
            # Go up
            try:
                current = parent.pop()
            except IndexError:
                current = current

    return d


def generate_random_list(length):
    numbers = range(0, 100)
    return [choice(numbers) for _ in range(length)]


def generate_random_set(iterations):
    numbers = range(0, 100)
    return set([choice(numbers) for _ in range(iterations)])


def _generate_random_data_structure(no_set=False, _type=None):
    if no_set:
        option = randint(0, 89)
    else:
        option = randint(0, 100)

    if _type:
        if _type == set:
            option = 95
        elif _type == list:
            option = 60
        elif _type == dict:
            option = 30

    if 0 <= option < 45:
        return generate_random_dictionary(1)
    elif 45 <= option < 90:
        return generate_random_list(1)
    else:
        return generate_random_set(randint(0, 20))


def generate_random_data_structure(iterations, _type=None):
    d = _generate_random_data_structure(no_set=True, _type=_type)

    def add_element(current):
        tmp = _generate_random_data_structure()
        if type(current) == list:
            current.insert(randint(0, len(current)-1), tmp)
        elif type(current) == dict:
            random_key = generate_random_string(randint(1, 10))
            current[random_key] = tmp

    parent = []
    current = d
    for _ in range(iterations):
        option = randint(0, 100)
        if 0 <= option < 40:
            # Add key
            add_element(current)
        elif 40 <= option < 80:
            # Go to key
            if type(current) == dict:
                key = choice(current.keys())
            elif type(current) == list:
                key = choice(range(len(current)))

            if type(current[key]) == dict or type(current[key]) == list:
                parent.append(current)
                current = current[key]
            else:
                add_element(current)
        elif 80 <= option <= 100:
            # Go up
            try:
                current = parent.pop()
            except IndexError:
                current = current

    return d


class DictPatchFunctionTest(unittest.TestCase):
    def test_dict_patch_process(self):
        for _ in range(100):
            first = generate_random_dictionary(10)
            second = generate_random_dictionary(10)

            diffs = list(diff(first, second))

            res = patch(diffs, first)
            rev = revert(diffs, second)

            self.assertEqual(res, second)
            self.assertEqual(rev, first)


class ListPatchFunctionTest(unittest.TestCase):
    def test_list_patch_process(self):
        for _ in range(100):
            first = generate_random_list(randint(1, 100))
            second = generate_random_list(randint(1, 100))

            diffs = list(diff(first, second))

            res = patch(diffs, first)
            rev = revert(diffs, second)

            self.assertEqual(res, second)
            self.assertEqual(rev, first)


class SetPatchFunctionTest(unittest.TestCase):
    def test_set_patch_process(self):
        for _ in range(100):
            first = generate_random_set(randint(1, 100))
            second = generate_random_set(randint(1, 100))

            diffs = list(diff(first, second))

            res = patch(diffs, first)
            rev = revert(diffs, second)

            self.assertEqual(res, second)
            self.assertEqual(rev, first)


from dictdiffer.extractors import get_default_extractors, SequenceExtractor


class SequencePatchFunctionTest(unittest.TestCase):
    def test_sequence_patch_process(self):
        for _ in range(100):
            first = generate_random_list(randint(1, 100))
            second = generate_random_list(randint(1, 100))

            e = get_default_extractors()
            e[list] = SequenceExtractor

            diffs = list(diff(first, second, extractors=e))

            res = patch(diffs, first)
            rev = revert(diffs, second)

            self.assertEqual(res, second)
            self.assertEqual(rev, first)


class PatchFunctionTest(unittest.TestCase):
    def test_patch_process_list(self):
        for _ in range(1000):
            first = generate_random_data_structure(randint(1, 100))
            second = generate_random_data_structure(randint(1, 100),
                                                    type(first))

            diffs = list(diff(first, second))

            res = patch(diffs, first)
            rev = revert(diffs, second)

            self.assertEqual(res, second)
            self.assertEqual(rev, first)

    def test_patch_process_list_expand(self):
        for _ in range(1000):
            first = generate_random_data_structure(randint(1, 100))
            second = generate_random_data_structure(randint(1, 100),
                                                    type(first))

            diffs = list(diff(first, second, expand=True))

            res = patch(diffs, first)
            rev = revert(diffs, second)

            self.assertEqual(res, second)
            self.assertEqual(rev, first)

    def test_patch_process_sequence(self):
        for _ in range(1000):
            self.maxDiff = None

            first = generate_random_data_structure(randint(1, 100))
            second = generate_random_data_structure(randint(1, 100),
                                                    type(first))

            e = get_default_extractors()
            e[list] = SequenceExtractor

            diffs = list(diff(first, second, extractors=e))

            res = patch(diffs, first)
            rev = revert(diffs, second)

            self.assertEqual(res, second)
            self.assertEqual(rev, first)

    def test_patch_process_sequence_expand(self):
        for _ in range(1000):
            self.maxDiff = None

            first = generate_random_data_structure(randint(1, 100))
            second = generate_random_data_structure(randint(1, 100),
                                                    type(first))

            e = get_default_extractors()
            e[list] = SequenceExtractor

            diffs = list(diff(first, second, extractors=e, expand=True))

            res = patch(diffs, first)
            rev = revert(diffs, second)

            self.assertEqual(res, second)
            self.assertEqual(rev, first)
