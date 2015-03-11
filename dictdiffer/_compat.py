# This file is part of Dictdiffer.
#
# Copyright (C) 2015 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Python compatibility definitions."""

import sys


if sys.version_info[0] == 3:  # pragma: no cover (Python 2/3 specific code)
    string_types = str,
    text_type = str
    PY2 = False
else:  # pragma: no cover (Python 2/3 specific code)
    string_types = basestring,
    text_type = unicode
    PY2 = True
