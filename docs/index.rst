============
 Dictdiffer
============
.. currentmodule:: dictdiffer

.. raw:: html

    <p style="height:22px; margin:0 0 0 2em; float:right">
        <a href="https://travis-ci.org/inveniosoftware/dictdiffer">
            <img src="https://travis-ci.org/inveniosoftware/dictdiffer.png?branch=master"
                 alt="travis-ci badge"/>
        </a>
        <a href="https://coveralls.io/r/inveniosoftware/dictdiffer">
            <img src="https://coveralls.io/repos/inveniosoftware/dictdiffer/badge.png?branch=master"
                 alt="coveralls.io badge"/>
        </a>
    </p>

Dictdiffer is a helper module that helps you to diff and patch
dictionaries.

Installation
============

Dictdiffer is on PyPI so all you need is:

.. code-block:: console

    $ pip install dictdiffer


Usage
=====

Let's start with an example on how to find the diff between two
dictionaries using :func:`.diff` method:

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
        ('change', ['settings', 'assignees', 2], (201, 202)),
        ('remove', 'settings.assignees', []),
        ('add', 'stargazers', [(2, '/users/40')]),
        ('remove', 'stargazers', []),
        ('change', 'title', ('hello', 'hellooo'))]


Now we can apply the diff result with :func:`.patch` method:

.. code-block:: python

    result = diff(first, second)
    patched = patch(result, first)

    assert patched == second


Also we can swap the diff result with :func:`.swap` method:

.. code-block:: python

    result = diff(first, second)
    swapped = swap(result)

    assert list(swapped) == [
        ('change', ['settings', 'assignees', 2], (202, 201)),
        ('add', 'settings.assignees', []),
        ('remove', 'stargazers', [(2, '/users/40')]),
        ('add', 'stargazers', []),
        ('change', 'title', ('hellooo', 'hello'))]


Let's revert the last changes:

.. code-block:: python

    reverted = revert(result, patched)
    assert reverted == first


API
===

.. automodule:: dictdiffer
   :members:

.. include:: ../CHANGES

Contributing
============

Bug reports, feature requests, and other contributions are welcome.
If you find a demonstrable problem that is caused by the code of this
library, please:

1. Search for `already reported problems
   <https://github.com/inveniosoftware/dictdiffer/issues>`_.
2. Check if the issue has been fixed or is still reproducible on the
   latest `master` branch.
3. Create an issue with **a test case**.

If you create a feature branch, you can run the tests to ensure everything is
operating correctly:

.. code-block:: console

    $ ./run-tests.sh

    ...

    Name         Stmts   Miss  Cover
    --------------------------------
    dictdiffer      87      0   100%

    ...

    52 passed, 2 skipped in 0.44 seconds

License
=======

.. include:: ../LICENSE

.. include:: ../AUTHORS
