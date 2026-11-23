# SPDX-License-Identifier: MIT

"""Match sequence positions without requiring hashable values."""


def ordered_matches(first_size, second_size, equal):
    """Yield an LCS of index pairs using linear auxiliary space.

    ``equal(i, j)`` compares values at the two positions. Common prefixes and
    suffixes avoid quadratic work for a single insertion into a long list.
    """
    def lengths(first_indices, second_indices):
        row = [0] * (len(second_indices) + 1)
        for i in first_indices:
            diagonal = 0
            for offset, j in enumerate(second_indices, 1):
                previous = row[offset]
                if equal(i, j):
                    row[offset] = diagonal + 1
                else:
                    row[offset] = max(row[offset], row[offset - 1])
                diagonal = previous
        return row

    def match(a, b, c, d):
        while a < b and c < d and equal(a, c):
            yield a, c
            a += 1
            c += 1
        suffix = 0
        while a < b and c < d and equal(b - 1, d - 1):
            b -= 1
            d -= 1
            suffix += 1
        if b - a == 1:
            for j in range(c, d):
                if equal(a, j):
                    yield a, j
                    break
        elif a < b and c < d:
            middle = (a + b) // 2
            left = lengths(range(a, middle), range(c, d))
            right = lengths(range(b - 1, middle - 1, -1),
                            range(d - 1, c - 1, -1))
            split = max(range(d - c + 1),
                        key=lambda k: left[k] + right[d - c - k]) + c
            # Do not retain the rows in recursive generator frames.
            del left, right
            yield from match(a, middle, c, split)
            yield from match(middle, b, split, d)
        for offset in range(suffix):
            yield b + offset, d + offset

    return match(0, first_size, 0, second_size)


def unordered_matches(first_size, second_size, equal):
    """Return a maximum one-to-one matching, preserving duplicate counts.

    Augmenting paths handle overlapping numeric tolerances, for which greedy
    matching can incorrectly report a difference. The search is iterative so
    a long reassignment chain does not consume the Python recursion limit.
    """
    first = [-1] * first_size
    second = [-1] * second_size
    for start in range(first_size):
        queue = [start]
        parents = {}
        found = False
        for i in queue:
            for j in range(second_size):
                if j in parents or not equal(i, j):
                    continue
                parents[j] = i
                if second[j] < 0:
                    while j >= 0:
                        i = parents[j]
                        previous = first[i]
                        first[i] = j
                        second[j] = i
                        j = previous
                    found = True
                    break
                queue.append(second[j])
            if found:
                break
    return first, second
