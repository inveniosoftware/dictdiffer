from copy import deepcopy

class DictDiffer(object):
    """ Base Class for a DictDiffer

    To add also diff functions for other types like strings or whatever, just
    subclass ``DictDiffer`` and provide methodes with a name pattern like
    "diff_<new implemented type.__name__>", then it will be called for this type.

    Almost all the logic is taken from the dictdiffer_ module from Fatih
    Erikli, but the implementation as a class has the advantage of making
    custom diffs easy and even has better performance[#1]_

    .. dictdiffer: https://github.com/fatiherikli/dictdiffer
    .. [#1] run benchmarking.py if you don't believe me

    """
    ADD = 'add'
    REMOVE = 'remove'
    PUSH = 'push'
    PULL = 'pull'
    CHANGE = 'change'
    METHODS = (ADD,REMOVE,PUSH,CHANGE,PULL)
    SEP = '.'
    def __init__(self):
        self.patchers = {x:getattr(self,'_patch_%s'%x) for x in self.METHODS}
        self.swappers = {x:getattr(self,'_swap_%s'%x) for x in self.METHODS}

    def _join_nodes(self,node):
        """ joins keys of subdictionaries """
        return self.SEP.join(node)

    def _set_nodes(self,destination,lookup,value):
        keys = lookup.split(self.SEP)
        if len(keys) > 1:
            dest = destination
            for key in keys[:-1]:
                dest = dest[key]
            dest[keys[-1]] = value
        else:
            destination[keys[0]] = value

    def _lookup_nodes(self,source,lookup,parent=None):
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

    def diff_dict(self,first,second,node):
        """ creates a diff of a dictionary """
        # calculate difference in keys
        firstset = frozenset(first)
        secondset = frozenset(second)
        intersection = firstset.intersection(secondset)
        addition = secondset - intersection
        deletion = firstset - intersection
        # now produce the nodes
        if addition:
            yield self.ADD,self._join_nodes(node),[(key,second[key]) for key in addition]

        if deletion:
            yield self.REMOVE,self._join_nodes(node),[(key,first[key]) for key in deletion]

        for key in intersection:
            recurred = self.diff(first[key],second[key],node=node+[key])
            for diff in recurred:
                yield diff

            # python 3
            #yield from self.diff(first[key],second[key],node=node+[key])

    def diff_list(self,first,second,node):
        """ creates a diff of a list """
        addition = [k for k in second if not k in first]
        deletion = [k for k in first if not k in second]
        if addition:
            yield self.PUSH, self._join_nodes(node), addition
        if deletion:
            yield self.PULL, self._join_nodes(node), deletion

    def diff_generic(self,first,second,node):
        """ creates a diff of all the other types not implemented """
        if first != second:
            yield self.CHANGE, self._join_nodes(node), (first,second)

    def diff(self,first,second,node=[]):
        if type(first) == type(second):
            return getattr(self,'diff_%s'%type(first).__name__,self.diff_generic)(first,second,node)
        else:
            return self.diff_generic(first,second,node)

    def _patch_add(self,destination,node,changes):
        for key, value in changes:
            self._lookup_nodes(destination,node)[key] = value

    def _patch_change(self,destination,node,changes):
        dest = self._lookup_nodes(destination,node,parent=True)
        try:
            #dest[dest.keys()[0]] = changes[0]
            self._set_nodes(destination,node,changes[1])
        except Exception as e:
            print(node,e)

    def _patch_remove(self,destination,node,changes):
        for key,value in changes:
            del self._lookup_nodes(destination,node)[key]

    def _patch_pull(self,destination,node,changes):
        dest = self._lookup_nodes(destination,node)
        for value in changes:
            dest.remove(value)

    def _patch_push(self,destination,node,changes):
        dest = self._lookup_nodes(destination,node)
        for value in changes:
            dest.append(value)

    def patch(self,diff_result,destination,copy=True):
        if copy:
            dest = deepcopy(destination)
        else:
            dest = destination
        for method, node,changes in diff_result:
            self.patchers[method](dest,node,changes)
        return dest

    def _swap_push(self,node , changes):
        return self.PULL, node, changes

    def _swap_pull(self,node, changes):
        return self.PUSH, node, changes

    def _swap_add(self,node, changes):
        return self.REMOVE, node, changes

    def _swap_remove(self,node, changes):
        return self.ADD, node, changes

    def _swap_change(self,node, changes):
        first, second = changes
        return self.CHANGE, node, (second, first)

    def swap(self,diff_result):
        for method, node, change in diff_result:
            yield self.swappers[method](node,change)

    def revert(self,diff_result,destination,copy=True):
        return self.patch(self.swap(diff_result),destination,copy=copy)
