#!/bin/sh
pep257 dictdiffer.py
sphinx-build -qnNW docs docs/_build/html
python setup.py test
