#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2014, 2016 CERN.
# Copyright (C) 2019 ETH Zurich, Swiss Data Science Center, Jiri Kuncar.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

python -m check_manifest --ignore ".*-requirements.txt"
python -m sphinx.cmd.build -qnNW docs docs/_build/html
python -m pytest
python -m sphinx.cmd.build -qnNW -b doctest docs docs/_build/doctest
