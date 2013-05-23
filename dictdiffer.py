ADD, REMOVE, PUSH, PULL, CHANGE = 'add', 'remove', 'push', 'pull', 'change'


def diff(old, new, node=None):
    node = node or []
    dotted_node = '.'.join(node)
    old_set = set(old)
    new_set = set(new)
    intersect = new_set & old_set
    addition = list(new_set - intersect)
    deletion = list(old_set - intersect)

    if isinstance(old, dict):
        if addition:
            yield ADD, dotted_node, addition

        if deletion:
            yield REMOVE, dotted_node, deletion

        for key in intersect:
            old_value = old[key]
            new_value = new[key]
            if type(old_value) is type(new_value):
                for diffed in diff(old_value,
                                   new_value,
                                   node=node + [key]):
                    yield diffed

    elif isinstance(old, list):
        if addition:
            yield PUSH, dotted_node, addition
        if deletion:
            yield PULL, dotted_node, deletion
    else:
        if old != new:
            yield CHANGE, dotted_node, new
