===================
 Dictdiffer v0.7.0
===================

Dictdiffer v0.7.0 was released on October 16, 2017.

About
-----

Dictdiffer is a helper module that helps you to diff and patch
dictionaries.

Incompatible changes
--------------------

- Fixes problem with diff results that reference the original structure by
  introduction of `deepcopy` for all possibly unhashable items. Thus the diff
  does not change later when the diffed structures change.

Improved features
-----------------

- Adds new option for patching and reverting patches in-place.
- Adds Python 3.6 to test matrix.

Bug fixes
---------

- Fixes the `ignore` argument when it contains a unicode value.

Installation
------------

   $ pip install dictdiffer==0.7.0

Documentation
-------------

   http://dictdiffer.readthedocs.io/en/v0.7.0

Happy hacking and thanks for flying Dictdiffer.

| Invenio Development Team
|   Email: info@inveniosoftware.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/dictdiffer
