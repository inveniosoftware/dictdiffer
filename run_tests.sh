#!/bin/sh
pep257 dictdiffer.py
sphinx-build -qnNW docs docs/_build/html
py.test --clearcache --pep8 --doctest-modules --cov=dictdiffer.py dictdiffer.py tests.py
