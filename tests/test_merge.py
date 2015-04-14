# This file is part of Dictdiffer.
#
# Copyright (C) 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

import unittest

from dictdiffer.merge import Merger, UnresolvedConflictsException


class MergerTest(unittest.TestCase):
    def test_run(self):
        lca = {'changeme': 'Jo'}
        first = {'changeme': 'Joe'}
        second = {'changeme': 'John'}

        m = Merger(lca, first, second, {})

        self.assertRaises(UnresolvedConflictsException, m.run)

    def test_continue_run(self):
        def take_first(conflict, _, __, ___):
            conflict.take = [('f', x) for x
                             in range(len(conflict.first_patch.patches))]
            return True

        lca = {'changeme': 'Jo'}
        first = {'changeme': 'Joe'}
        second = {'changeme': 'John'}

        m = Merger(lca, first, second, {})

        try:
            m.run()
        except UnresolvedConflictsException:
            pass

        m.continue_run(['f'])

        self.assertEqual(m.unified_patches,
                         [('change', 'changeme', ('Jo', 'Joe'))])


if __name__ == '__main__':
    unittest.main()
