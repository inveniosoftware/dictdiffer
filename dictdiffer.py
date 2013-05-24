(ADD, REMOVE, PUSH, PULL, CHANGE) = (
    'add', 'remove', 'push', 'pull', 'change')


def diff(first, second, node=None):
    """Compares two dictionary object, and returns a diff result.

        >>> result = diff({'a':'b'}, {'a':'c'})
        >>> list(result)
        [('change', 'a', 'c')]

    """
    node = node or []
    dotted_node = '.'.join(node)

    first_set = set(first)
    second_set = set(second)
    intersection = second_set & first_set
    addition = list(second_set - intersection)
    deletion = list(first_set - intersection)

    def diff_dict():
        """Compares if object is a dictionary. Callees again the parent
        function as recursive if dictionary have child objects.
        Yields `add` and `remove` flags."""
        if addition:
            yield ADD, dotted_node, [
                # for additions, returns a list that consist with two-pairs.
                (key, second[key]) for key in addition]

        if deletion:
            # for deletions, returns the list of removed keys
            yield REMOVE, dotted_node, deletion

        for key in intersection:
            first_value = first[key]
            second_value = second[key]

            # if type is not changed, callees again diff function to compare.
            # otherwise, the change will be handled as `change` flag.
            if type(first_value) is type(second_value):

                recurred = diff(
                    first_value,
                    second_value,
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
            yield CHANGE, dotted_node, second

    differs = {
        dict: diff_dict,
        list: diff_list
    }

    differ = differs.get(type(first))
    return (differ or diff_otherwise)()
