### Dictdiffer

Dictdiffer is a helper module that helps you to diff and patch dictionaries.

#### dictdiffer.diff
Compares two dictionary object and returns a diff result.

#### dictdiffer.patch
Applies the diff result to the old dictionary.

#### dictdiffer.swap
Swaps the diff result to revert changes.

#### dictdiffer.revert
A shortcut function that swaps and patches the diff result to
destination dictionary.

### Examples

```python
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
```

Now we can apply the diff result with `patch` method.

```python
result = diff(first, second)
patched = patch(result, first)

assert patched == second
```

Also we can swap the diff result with `swap` method.

```python
result = diff(first, second)
swapped = swap(result)

assert list(swapped) == [
    ('pull', 'settings.assignees', [202]),
    ('push', 'settings.assignees', [201]),
    ('pull', 'stargazers', ['/users/40']),
    ('change', 'title', ('hellooo', 'hello'))]
```

Let's revert the last changes.

```python
reverted = revert(result, patched)
assert reverted == first
```

### Contribution & Tests

After your changes, you could run the tests to ensure everything is
operating correctly.

    $ source run_tests.sh
    Ran 15 tests in 0.002s

    Name         Stmts   Miss  Cover   Missing
    ------------------------------------------
    dictdiffer      74      0   100%
    ------------------------------------------
    TOTAL           74      0   100%
