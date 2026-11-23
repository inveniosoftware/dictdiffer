==========
Dictdiffer
==========
.. currentmodule:: dictdiffer

.. image:: https://github.com/inveniosoftware/dictdiffer/workflows/CI/badge.svg
        :target: https://github.com/inveniosoftware/dictdiffer/actions

.. image:: https://img.shields.io/coveralls/inveniosoftware/dictdiffer.svg
        :target: https://coveralls.io/r/inveniosoftware/dictdiffer

.. image:: https://img.shields.io/github/tag/inveniosoftware/dictdiffer.svg
        :target: https://github.com/inveniosoftware/dictdiffer/releases

.. image:: https://img.shields.io/pypi/dm/dictdiffer.svg
        :target: https://pypi.python.org/pypi/dictdiffer

.. image:: https://img.shields.io/github/license/inveniosoftware/dictdiffer.svg
        :target: https://github.com/inveniosoftware/dictdiffer/blob/master/LICENSE

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

List comparison
===============

Lists are compared by index by default. Use ``align_lists=True`` to align
unchanged items and report insertions and removals at their actual positions:

.. doctest::

    >>> from dictdiffer import diff, patch, revert
    >>> first = ['one', 'two', 'three']
    >>> second = ['two', 'three']
    >>> changes = list(diff(first, second, align_lists=True))
    >>> changes
    [('remove', '', [(0, 'one')])]
    >>> patch(changes, first) == second
    True
    >>> revert(changes, second) == first
    True

Replacement gaps are still compared recursively, so editing one field of a
dictionary in a list produces a field change. Alignment uses a longest common
subsequence, supports unhashable items and honours ``ignore``, ``tolerance`` and
``absolute_tolerance``. Index-qualified ignored fields refer to target positions
when aligning. Equal prefixes and suffixes are scanned directly; the remaining
alignment takes quadratic time and linear auxiliary space in the list lengths.

Use ``ignore_order=True`` to compare lists as multisets, recursively, while
retaining duplicate counts. This takes precedence over ``align_lists``:

.. doctest::

    >>> list(diff([{'a': 1}, {'b': 2}], [{'b': 2}, {'a': 1}], ignore_order=True))
    []
    >>> first, second = [1, 2, 1], [2, 3, 1]
    >>> changes = list(diff(first, second, ignore_order=True))
    >>> patched = patch(changes, first)
    >>> patched
    [1, 2, 3]
    >>> list(diff(patched, second, ignore_order=True))
    []
    >>> revert(changes, patched) == first
    True

An unordered patch retains matched items in source order and appends unmatched
target items. It need not reproduce the target's order. Pass the actual patched
value to ``revert`` to restore the original order. Matching respects numeric
tolerances and ignored dictionary keys; index-qualified ignored fields refer to
the candidate's position in the first list. A maximum one-to-one matching avoids
false differences when numeric tolerances overlap. It uses linear auxiliary
space, with worst-case cubic time for equal-length lists. Prefer the default
positional comparison when order matters and the lists are large.

Both options work with ``expand``, ``dot_notation`` and ``path_limit``. As with
ordinary diffs, ignored or numerically equivalent values are retained rather
than replaced. Diff payloads remain deep copies.

``swap`` reverses operation order as well as addition/removal batches, ensuring
that edits to shifted list indices and nested additions are undone correctly.
It consumes the complete input iterator before yielding its first operation.

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
