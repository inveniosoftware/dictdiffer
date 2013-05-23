(ADD, REMOVE, PUSH, PULL, CHANGE) = (
    'add', 'remove', 'push', 'pull', 'change')


def diff(first, second, node=None):
    node = node or []
    dotted_node = '.'.join(node)

    first_set = set(first)
    second_set = set(second)
    intersection = second_set & first_set
    addition = list(second_set - intersection)
    deletion = list(first_set - intersection)

    def diff_dict():
        if addition:
            yield ADD, dotted_node, addition

        if deletion:
            yield REMOVE, dotted_node, deletion

        for key in intersection:
            first_value = first[key]
            second_value = second[key]
            if type(first_value) is type(second_value):
                recurred = diff(
                    first_value,
                    second_value,
                    node=node + [key])
                for diffed in recurred:
                    yield diffed

    def diff_list():
        if addition:
            yield PUSH, dotted_node, addition

        if deletion:
            yield PULL, dotted_node, deletion

    def diff_otherwise():
        if first != second:
            yield CHANGE, dotted_node, second

    differ = {
        dict: diff_dict,
        list: diff_list,
    }.get(type(first), diff_otherwise)

    return differ()
