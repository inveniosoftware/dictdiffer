==========
Dictdiffer
==========
.. currentmodule:: dictdiffer

.. raw:: html

    <p style="height:22px; margin:0 0 0 2em; float:right">
        <a href="https://travis-ci.org/inveniosoftware/dictdiffer">
            <img src="https://travis-ci.org/inveniosoftware/dictdiffer.svg?branch=master"
                 alt="travis-ci badge"/>
        </a>
        <a href="https://coveralls.io/r/inveniosoftware/dictdiffer">
            <img src="https://coveralls.io/repos/inveniosoftware/dictdiffer/badge.svg?branch=master"
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
        ('add', 'stargazers', [(2, '/users/40')]),
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
        ('remove', 'stargazers', [(2, '/users/40')]),
        ('change', 'title', ('hellooo', 'hello'))]


Let's revert the last changes:

.. code-block:: python

    result = diff(first, second)
    reverted = revert(result, patched)
    assert reverted == first

A tolerance can be used to consider closed values as equal.
The tolerance parameter only applies for int and float.

Let's try with a tolerance of 10% with the values 10 and 10.5:

.. code-block:: python

    first = {'a': 10.0}
    second = {'a': 10.5}

    result = diff(first, second, tolerance=0.1)

    assert list(result) == []

Now with a tolerance of 1%:

.. code-block:: python

    result = diff(first, second, tolerance=0.01)

    assert list(result) == ('change', 'a', (10.0, 10.5))

API
===

.. automodule:: dictdiffer
   :members:

.. include:: ../CHANGES

.. include:: ../CONTRIBUTING.rst

License
=======

.. include:: ../LICENSE

.. include:: ../AUTHORS
