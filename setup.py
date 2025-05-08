# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2014, 2015, 2016 CERN.
# Copyright (C) 2017 ETH Zurich, Swiss Data Science Center, Jiri Kuncar.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dictdiffer is a library that helps you to diff and patch dictionaries."""

from __future__ import absolute_import, print_function

import os
import re

from setuptools import find_packages, setup

readme = "Dictdiffer is a helper module that helps you to diff and patch dictionaries."
history = open('CHANGES').read()

tests_require = [
    'coverage>=4.0',
    'mock>=1.3.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov==2.6.1',
    'pytest-pep8>=1.0.6',
    'pytest~=4.6; python_version == "2.7"',
    'pytest~=6.0,>=6.2.5; python_version >= "3"'
]

extras_require = {
    'numpy': [
        'numpy>=1.11.0',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for key, reqs in extras_require.items():
    if ':' == key[0]:
        continue
    extras_require['all'].extend(reqs)

packages = find_packages()


# Get the version string. Cannot be done with import!
with open(os.path.join('dictdiffer', 'version.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

setup(
    name='inspire-dictdiffer',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    author='Invenio Collaboration',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/dictdiffer',
    packages=['dictdiffer'],
    zip_safe=False,
    extras_require=extras_require,
    tests_require=tests_require,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
)
