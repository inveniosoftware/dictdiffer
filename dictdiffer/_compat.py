# This file is part of Dictdiffer.
#
# Copyright (C) 2015, 2016 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Python compatibility definitions."""

import sys

if sys.version_info[0] == 3:  # pragma: no cover (Python 2/3 specific code)
    string_types = str,
    text_type = str
    num_types = int, float
    PY2 = False

    from collections.abc import MutableMapping, MutableSet, MutableSequence
    from itertools import zip_longest as _zip_longest
    izip_longest = _zip_longest
else:  # pragma: no cover (Python 2/3 specific code)
    string_types = basestring,
    text_type = unicode
    num_types = int, long, float
    PY2 = True

    from collections import MutableMapping, MutableSet, MutableSequence
    from itertools import izip_longest as _zip_longest
    izip_longest = _zip_longest
