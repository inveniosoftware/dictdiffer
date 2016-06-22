===================
 Dictdiffer v0.6.0
===================

Dictdiffer v0.6.0 was released on June 22, 2016.

About
-----

Dictdiffer is a helper module that helps you to diff and patch
dictionaries.

New features
------------

- Adds support for comparing NumPy arrays.  (#68)
- Adds support for comparing mutable mappings, sequences and sets from
  `collections.abs` module.  (#67)

Improved features
-----------------

- Updates package structure, sorts imports and runs doctests.

Bug fixes
---------

- Fixes order in which handled conflicts are unified so that the
  Merger's unified_patches can be always applied.

Installation
------------

   $ pip install dictdiffer==0.6.0

Documentation
-------------

   http://dictdiffer.readthedocs.org/en/v0.6.0

Happy hacking and thanks for flying Dictdiffer.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/dictdiffer
