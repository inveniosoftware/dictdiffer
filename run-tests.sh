#!/bin/sh
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

pydocstyle dictdiffer && \
isort -rc -c -df **/*.py && \
check-manifest --ignore ".travis-*,dictdiffer/version.py" && \
sphinx-build -qnNW docs docs/_build/html && \
python setup.py test
