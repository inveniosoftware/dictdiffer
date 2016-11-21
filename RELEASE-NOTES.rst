===================
 Dictdiffer v0.6.1
===================

Dictdiffer v0.6.1 was released on November 22, 2016.

About
-----

Dictdiffer is a helper module that helps you to diff and patch
dictionaries.

Improved features
-----------------

- Improves API documentation for `ignore` argument in `diff` function.
  (#79)
- Executes doctests during PyTest invocation.

Bug fixes
---------

- Changes order of items for REMOVE section of generated patches when
  `swap` is called so the list items are removed from the end. (#85)

Installation
------------

   $ pip install dictdiffer==0.6.1

Documentation
-------------

   http://dictdiffer.readthedocs.io/en/v0.6.1

Happy hacking and thanks for flying Dictdiffer.

| Invenio Development Team
|   Email: info@inveniosoftware.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/dictdiffer
