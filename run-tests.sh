#!/bin/sh
#
# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2014 CERN.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

pep257 dictdiffer
sphinx-build -qnNW docs docs/_build/html
python setup.py test
