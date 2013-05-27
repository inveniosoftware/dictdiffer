import copy

(ADD, REMOVE, PUSH, PULL, CHANGE) = (
    'add', 'remove', 'push', 'pull', 'change')


class Differ(object):
    """
    Compares two dictionary object, and returns a diff result.

        >>> differ = Differ()
        >>> result = differ({'a':'b'}, {'a':'c'})
        >>> list(result)
        [('change', 'a', ('b', 'c'))]

    """

    # dictionaries are not hashable, we can't use sets
    def intersection(self, first, second):
        """Returns the intersection of given objects"""
        return [k for k in first if k in second]

    def addition(self, first, second):
        """Returns the added items of second object"""
        return [k for k in second if not k in first]

    def deletion(self, first, second):
        """Returns deleted items from first object"""
        return [k for k in first if not k in second]

    def dotted(self, node):
        """Returns dotted notation of node"""
        return '.'.join(node)

    def diff_dict(self, first, second, node):
        """Compares if object is a dictionary. Callees again the parent
        function as recursive if dictionary have child objects.
        Yields `add` and `remove` flags."""
        addition = self.addition(first, second)
        deletion = self.deletion(first, second)
        dotted_node = self.dotted(node)

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

        for key in self.intersection(first, second):
            # if type is not changed, callees again diff function to compare.
            # otherwise, the change will be handled as `change` flag.
            if type(first[key]) is type(second[key]):

                recurred = self(
                    first[key],
                    second[key],
                    node=node + [key])

                for diffed in recurred:
                    yield diffed

    def diff_list(self, first, second, node):
        """Compares if objects are list. Yields `push` and `pull` flags."""
        addition = self.addition(first, second)
        deletion = self.deletion(first, second)
        dotted_node = self.dotted(node)

        if addition:
            # the addition will be consist with the list of added values.
            yield PUSH, dotted_node, addition

        if deletion:
            # for deletions, returns the list of removed items
            yield PULL, dotted_node, deletion

    def diff_otherwise(self, first, second, node):
        """Compares string and integer types. Yields `change` flag."""
        if first != second:
            yield CHANGE, self.dotted(node), (first, second)

    def __call__(self, first, second, node=None):
        """Calles the differ method by the type of object that
        will be compared"""

        assert type(first) is type(second), \
            "You can't compare different typed objects."

        differ = {
            dict: self.diff_dict,
            list: self.diff_list
        }.get(type(first)) or self.diff_otherwise

        return differ(first, second, node or [])


diff = Differ()


class Patcher(object):
    def __call__(self, diff_result, destination):
        """
        Patches the diff result to the old dictionary.

            >>> patcher = Patcher()
            >>> patcher([('push', 'numbers', [2, 3])], {'numbers': []})
            {'numbers': [2, 3]}
            >>> patcher([('pull', 'numbers', [1])], {'numbers': [1, 2, 3]})
            {'numbers': [2, 3]}

        """
        destination = copy.deepcopy(destination)
        for action, node, changes in diff_result:
            getattr(self, action)(destination, node, changes)
        return destination

    def add(self, destination, node, changes):
        for key, value in changes:
            dot_lookup(destination, node)[key] = value

    def change(self, destination, node, changes):
        dest = dot_lookup(destination, node, parent=True)
        last_node = node.split('.')[-1]
        _, value = changes
        dest[last_node] = value

    def remove(self, destination, node, changes):
        for key, _ in changes:
            del dot_lookup(destination, node)[key]

    def pull(self, destination, node, changes):
        dest = dot_lookup(destination, node)
        for val in changes:
            dest.remove(val)

    def push(self, destination, node, changes):
        dest = dot_lookup(destination, node)
        for val in changes:
            dest.append(val)


patch = Patcher()


class Swapper(object):
    """
    Swaps the diff result with the following mapping

        pull -> push
        push -> pull
        remove -> add
        add -> remove

    In addition, swaps the changed values for `change` flag.

        >>> swapper = Swapper()
        >>> swapped = swapper([('add', 'a.b.c', ('a', 'b'))])
        >>> next(swapped)
        ('remove', 'a.b.c', ('a', 'b'))

        >>> swapped = swapper([('change', 'a.b.c', ('a', 'b'))])
        >>> next(swapped)
        ('change', 'a.b.c', ('b', 'a'))

    """

    def __call__(self, diff_result):
        for action, node, change in diff_result:
            yield getattr(self, action)(node, change)

    def push(self, node, changes):
        return PULL, node, changes

    def pull(self, node, changes):
        return PUSH, node, changes

    def add(self, node, changes):
        return REMOVE, node, changes

    def remove(self, node, changes):
        return ADD, node, changes

    def change(self, node, changes):
        first, second = changes
        return CHANGE, node, (second, first)


swap = Swapper()


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
