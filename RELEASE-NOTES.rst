===============================
 Dictdiffer v0.1.0 is released
===============================

Dictdiffer v0.1.0 was released on September 1, 2014.

About
-----

Dictdiffer is a helper module that helps you to diff and patch
dictionaries.

Dictdiffer was originally developed by Fatih Erikli.  It is now being
maintained by the Invenio collaboration.

What's new
----------

- Fix for list removal issues during patching caused by wrong
  iteration. (#10)
- Fix for issues with multiple value types for the same key. (#10)
- Fix for issues with strings handled as iterables. (#6)
- Fix for integer keys. (#12)
- Regression test for complex dictionaries. (#4)
- Better testing with Travis CI, tox, pytest, code coverage. (#10)
- Initial release of documentation on ReadTheDocs. (#21 #24)
- Support for Python 3. (#15)

Installation
------------

   $ pip install dictdiffer

Documentation
-------------

   http://dictdiffer.readthedocs.org/en/v0.1.0

Good luck and thanks for using Dictdiffer.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/dictdiffer
