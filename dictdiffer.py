import copy
import collections

(ADD, REMOVE, PUSH, PULL, CHANGE) = (
    'add', 'remove', 'push', 'pull', 'change')


def diff(first, second, node=None):
    """
    Compares two dictionary object, and returns a diff result.

        >>> result = diff({'a':'b'}, {'a':'c'})
        >>> list(result)
        [('change', 'a', ('b', 'c'))]

    """
    node = node or []
    dotted_node = '.'.join(node)

    if isinstance(first, collections.Iterable):
        # dictionaries are not hashable, we can't use sets
        intersection = [k for k in first if k in second]
        addition = [k for k in second if not k in first]
        deletion = [k for k in first if not k in second]

    def diff_dict():
        """Compares if object is a dictionary. Callees again the parent
        function as recursive if dictionary have child objects.
        Yields `add` and `remove` flags."""
        if addition:
            yield ADD, dotted_node, [
                # for additions, return a list that consist with
                # two-pair tuples.
                (key, second[key]) for key in addition]

        if deletion:
            yield REMOVE, dotted_node, [
                # for deletions, return the list of removed keys
                # and values.
                (key, first[key]) for key in deletion]

        for key in intersection:
            # if type is not changed, callees again diff function to compare.
            # otherwise, the change will be handled as `change` flag.
            recurred = diff(
                first[key],
                second[key],
                node=node + [key])

            for diffed in recurred:
                yield diffed

    def diff_list():
        """Compares if objects are list. Yields `push` and `pull` flags."""
        if addition:
            # the addition will be consist with the list of added values.
            yield PUSH, dotted_node, addition

        if deletion:
            # for deletions, returns the list of removed items
            yield PULL, dotted_node, deletion

    def diff_otherwise():
        """Compares string and integer types. Yields `change` flag."""
        if first != second:
            yield CHANGE, dotted_node, (first, second)

    differs = {
        dict: diff_dict,
        list: diff_list
    }

    differ = differs.get(type(first))
    return (differ or diff_otherwise)()


def patch(diff_result, destination):
    """
    Patches the diff result to the old dictionary.

        >>> patch([('push', 'numbers', [2, 3])], {'numbers': []})
        {'numbers': [2, 3]}

        >>> patch([('pull', 'numbers', [1])], {'numbers': [1, 2, 3]})
        {'numbers': [2, 3]}

    """
    destination = copy.deepcopy(destination)

    def add(node, changes):
        for key, value in changes:
            dot_lookup(destination, node)[key] = value

    def change(node, changes):
        dest = dot_lookup(destination, node, parent=True)
        last_node = node.split('.')[-1]
        _, value = changes
        dest[last_node] = value

    def remove(node, changes):
        for key, _ in changes:
            del dot_lookup(destination, node)[key]

    def pull(node, changes):
        dest = dot_lookup(destination, node)
        for val in changes:
            dest.remove(val)

    def push(node, changes):
        dest = dot_lookup(destination, node)
        for val in changes:
            dest.append(val)

    patchers = {
        PUSH: push,
        PULL: pull,
        REMOVE: remove,
        ADD: add,
        CHANGE: change
    }

    for action, node, changes in diff_result:
        patchers[action](node, changes)

    return destination


def swap(diff_result):
    """
    Swaps the diff result with the following mapping

        pull -> push
        push -> pull
        remove -> add
        add -> remove

    In addition, swaps the changed values for `change` flag.

        >>> swapped = swap([('add', 'a.b.c', ('a', 'b'))])
        >>> next(swapped)
        ('remove', 'a.b.c', ('a', 'b'))

        >>> swapped = swap([('change', 'a.b.c', ('a', 'b'))])
        >>> next(swapped)
        ('change', 'a.b.c', ('b', 'a'))

    """

    def push(node, changes):
        return PULL, node, changes

    def pull(node, changes):
        return PUSH, node, changes

    def add(node, changes):
        return REMOVE, node, changes

    def remove(node, changes):
        return ADD, node, changes

    def change(node, changes):
        first, second = changes
        return CHANGE, node, (second, first)

    swappers = {
        PUSH: push,
        PULL: pull,
        REMOVE: remove,
        ADD: add,
        CHANGE: change
    }

    for action, node, change in diff_result:
        yield swappers[action](node, change)


def revert(diff_result, destination):
    """
    A helper function that calles swap function to revert
    patched dictionary object.

        >>> first = {'a': 'b'}
        >>> second = {'a': 'c'}
        >>> revert(diff(first, second), second)
        {'a': 'b'}

    """
    return patch(swap(diff_result), destination)


def dot_lookup(source, lookup, parent=False):
    """
    A helper function that allows you to reach dictionary
    items with dot lookup (e.g. document.properties.settings)

        >>> dot_lookup({'a': {'b': 'hello'}}, 'a.b')
        'hello'

    If parent argument is True, returns the parent node of matched
    object.

        >>> dot_lookup({'a': {'b': 'hello'}}, 'a.b', parent=True)
        {'b': 'hello'}

    If node is empy value, returns the whole dictionary object.

        >>> dot_lookup({'a': {'b': 'hello'}}, '')
        {'a': {'b': 'hello'}}

    """
    if not lookup:
        return source

    value = source
    keys = lookup.split('.')

    if parent:
        keys = keys[:-1]

    for key in keys:
        value = value[key]
    return value
