==========
Dictdiffer
==========
.. currentmodule:: dictdiffer

Dictdiffer is a helper module that helps you to diff and patch
dictionaries.

Contents
--------

.. contents::
   :local:
   :backlinks: none


Installation
============

Dictdiffer is on PyPI so all you need is:

.. code-block:: console

    $ pip install dictdiffer


Examples
========

Let's start with finding the diff of two dictionaries using :func:`.diff`
method.

.. code-block:: python

    from dictdiffer import diff, patch, swap, revert

    first = {
        "title": "hello",
        "fork_count": 20,
        "stargazers": ["/users/20", "/users/30"],
        "settings": {
            "assignees": [100, 101, 201],
        }
    }

    second = {
        "title": "hellooo",
        "fork_count": 20,
        "stargazers": ["/users/20", "/users/30", "/users/40"],
        "settings": {
            "assignees": [100, 101, 202],
        }
    }

    result = diff(first, second)

    assert list(result) == [
        ('push', 'settings.assignees', [202]),
        ('pull', 'settings.assignees', [201]),
        ('push', 'stargazers', ['/users/40']),
        ('change', 'title', ('hello', 'hellooo'))]


Now we can apply the diff result with :func:`.patch` method.

.. code-block:: python

    result = diff(first, second)
    patched = patch(result, first)

    assert patched == second


Also we can swap the diff result with :func:`.swap` method.

.. code-block:: python

    result = diff(first, second)
    swapped = swap(result)

    assert list(swapped) == [
        ('pull', 'settings.assignees', [202]),
        ('push', 'settings.assignees', [201]),
        ('pull', 'stargazers', ['/users/40']),
        ('change', 'title', ('hellooo', 'hello'))]


Let's revert the last changes.

.. code-block:: python

    reverted = revert(result, patched)
    assert reverted == first


Contribution & Tests
====================

Bug reports, feature requests, or other contributions are welcome.
If you find a demonstrable problem that is caused by the code of this
library please:

1. Search for already reported problem using GitHub issue search.
2. Check if the issue has been fixed or is still reproducable on the
   latest `master` branch.
3. Create an issue with **a test case**.

After your changes, you could run the tests to ensure everything is
operating correctly.

.. code-block:: console

    $ ./run_tests.sh
    ...
    Name         Stmts   Miss  Cover
    --------------------------------
    dictdiffer      87      0   100%
    ...

API
===

This documentation is automatically generated from Dictdiffer's source
code.

.. automodule:: dictdiffer
   :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

