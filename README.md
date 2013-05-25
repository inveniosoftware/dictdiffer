Work in progress.

### Dictdiffer

Dictdiffer is a helper module that helps you to diff and patch dictionaries.

There are two function in dictdiffer module; diff and patch.

#### dictdiffer.diff
Compares two dictionary object and returns a diff result.

#### dictdiffer.patch
Applies the diff result to the old dictionary.

### Examples

```python

from dictdiffer import diff, patch

first = {
    "title": "hello",
    "fork_count": 20,
    "stargazers": ["/users/20", "/users/30"],
    "settings": {
        "is_public": True,
        "assignees": [100, 101, 201],
    }
}


second = {
    "title": "hellooo",
    "fork_count": 20,
    "stargazers": ["/users/20", "/users/30", "/users/40"],
    "settings": {
        "is_public": False,
        "assignees": [100, 101, 202],
    }
}

result = diff(first, second)

assert list(result) == [
    ('change', 'settings.is_public', False),
    ('push', 'settings.assignees', [202]),
    ('pull', 'settings.assignees', [201]),
    ('push', 'stargazers', ['/users/40']),
    ('change', 'title', 'hellooo')]


# Now we can apply diff result

result = diff(first, second)
patched = patch(result, first)

assert patched == second
```

### Todo

 - Revisions
 - Revert

### Contribution & Tests

After your changes, you could run the tests to ensure everything is
operating correctly.

    $ source run_tests.sh

    Ran 11 tests in 0.002s

    OK
    Name         Stmts   Miss  Cover   Missing
    ------------------------------------------
    dictdiffer      64      0   100%
    ------------------------------------------
    TOTAL           64      0   100%
