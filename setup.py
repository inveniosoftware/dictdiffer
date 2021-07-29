# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2014, 2015, 2016 CERN.
# Copyright (C) 2017, 2019 ETH Zurich, Swiss Data Science Center, Jiri Kuncar.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dictdiffer is a library that helps you to diff and patch dictionaries."""

from __future__ import absolute_import, print_function

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

tests_require = [
    'check-manifest>=0.42',
    'mock>=1.3.0',
    'pytest==5.4.3;python_version<="3.5"',
    'pytest>=6;python_version>"3.5"',
    'pytest-cov>=2.10.1',
    'pytest-isort>=1.2.0',
    'pytest-pycodestyle>=2;python_version<="3.5"',
    'pytest-pycodestyle>=2.2.0;python_version>"3.5"',
    'pytest-pydocstyle>=2;python_version<="3.5"',
    'pytest-pydocstyle>=2.2.0;python_version>"3.5"',
    'sphinx>=3',
    'tox>=3.7.0',
]

extras_require = {
    'docs': [
        'Sphinx>=3',
        'sphinx-rtd-theme>=0.2',
    ],
    'numpy': [
        'numpy>=1.13.0;python_version<"3.7"',
        'numpy>=1.15.0;python_version<"3.8"',
        'numpy>=1.18.0;python_version<"3.9"',
        'numpy>=1.20.0;python_version>="3.9"',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for key, reqs in extras_require.items():
    if ':' == key[0]:
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.7',
    'setuptools_scm>=3.1.0',
]

packages = find_packages()

version_template = """\
# -*- coding: utf-8 -*-
# Do not change the format of this next line. Doing so risks breaking
# setup.py and docs/conf.py
\"\"\"Version information for dictdiffer package.\"\"\"

__version__ = {version!r}
"""

setup(
    name='dictdiffer',
    use_scm_version={
        'local_scheme': 'dirty-tag',
        'write_to': os.path.join('dictdiffer', 'version.py'),
        'write_to_template': version_template,
    },
    description=__doc__,
    long_description=readme,
    author='Invenio Collaboration',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/dictdiffer',
    project_urls={
        'Changelog': (
            'https://github.com/inveniosoftware/dictdiffer'
            '/blob/master/CHANGES'
        ),
        'Docs': 'https://dictdiffer.rtfd.io/',
    },
    packages=['dictdiffer'],
    zip_safe=False,
    extras_require=extras_require,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
)
