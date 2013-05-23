ADD, REMOVE, PUSH, PULL, CHANGE = 'add', 'remove', 'push', 'pull', 'change'


def diff(old, new, node=None):
    node = node or []
    old_set = set(old)
    new_set = set(new)
    intersect = new_set & old_set
    addition = new_set - intersect
    deletion = old_set - intersect

    if isinstance(old, dict):
        if addition:
            yield ADD, node, addition

        if deletion:
            yield REMOVE, node, deletion

        for key in intersect:
            if type(old[key]) is type(old[key]):
                for diffed in diff(old[key], new[key], node=node + [key]):
                    yield diffed

    elif isinstance(old, list):
        yield PUSH, node, addition
        yield PULL, node, deletion
    else:
        if old != new:
            yield CHANGE, node, new
