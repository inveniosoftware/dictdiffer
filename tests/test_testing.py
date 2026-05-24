# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

import unittest

import pytest

from dictdiffer.testing import assert_no_diff


class AssertNoDiffTest(unittest.TestCase):
    def test_passes(self):
        dict1 = {1: '1'}
        assert_no_diff(dict1, dict1)

    def test_raises_assertion_error(self):
        dict1 = {1: '1'}
        dict2 = {2: '2'}
        with pytest.raises(AssertionError):
            assert_no_diff(dict1, dict2)
