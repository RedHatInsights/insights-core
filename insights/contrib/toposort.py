#######################################################################
# Implements a topological sort algorithm.
#
# Copyright 2014 True Blade Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Notes:
#  Based on http://code.activestate.com/recipes/578272-topological-sort
#   with these major changes:
#    Added unittests.
#    Deleted doctests (maybe not the best idea in the world, but it cleans
#     up the docstring).
#    Moved functools import to the top of the file.
#    Changed assert to a ValueError.
#    Changed iter[items|keys] to [items|keys], for python 3
#     compatibility. I don't think it matters for python 2 these are
#     now lists instead of iterables.
#    Copy the input so as to leave it unmodified.
#    Renamed function from toposort2 to toposort.
#    Handle empty input.
#    Switch tests to use set literals.
#
########################################################################

from collections import defaultdict
from functools import reduce as _reduce
from sys import version_info

if isinstance(version_info, tuple):
    python_version = version_info[1]
else:
    python_version = version_info.major

__all__ = ['toposort', 'toposort_flatten']


def toposort_ancestor(data):
    """
    Dependencies are expressed as a dictionary whose keys are items
    and whose values are a set of dependent items. Output is a list of
    sets in topological order - i.e. first those items with no dependencies,
    then those with only dependencies in the previous set, and so on.

    The algorithm here is the 'inverse' of the (previous, standard) topological
    sort - it works by compiling the dictionary of ancestor sets and a count
    of dependents for each ancestor.  The 'ancestor' dictionary is the inverse
    of the 'dependency' dictionary - if 'a' depends on 'b', then 'b' is the
    ancestor of 'a'.  So if data = {'foo': {'bar', 'baz'}}, then ancestors =
    {'bar': {'foo'}, 'baz': {'foo}} and dependent_counts = {'foo': 2}.  At
    the start we also need to remember the set of 'terminators' - items that
    depend on other things, but on which nothing depends.

    The algorithm then works by iteratively finding the set of ancestors that
    do not have a dependent count, which are the ancestors which have no
    dependents.  That set is yielded, and then for each of those 'free'
    ancestors each of their dependents' counts is decremented (removing any
    ancestor whose dependent count reaches zero) and the ancestor is then
    removed from the ancestors dictionary.  This then iterates, with a
    smaller set of ancestors and dependent counts.  We exit when the set of
    'free' dependents is zero, either because we have traversed the graph
    completely, or we have found circular dependencies.  At this point we
    yield the 'terminators' set, because all other dependencies have been
    yielded already.
    """
    if not data:
        yield set()
        raise StopIteration

    ancestors = defaultdict(set)
    dependent_counts = defaultdict(int)
    for item, dependencies in data.items():
        for dep in dependencies:
            ancestors[dep].add(item)
            dependent_counts[item] += 1
    # It's quicker to remember the keys in the data that aren't required by
    # any other dependency, to emit last, than to add them into the ancestors
    # with empty sets.
    if python_version == 2:
        terminators = set(data.keys()) - set(ancestors.keys())
    else:
        terminators = data.keys() - ancestors.keys()
    # Iterate:
    ## print("Ancestors:", ancestors, "Dependents:", dependent_counts)
    while True:
        # The things that currently have no dependencies are ancestors that
        # are not mentioned in the set of dependents.
        if python_version == 2:
            have_no_dependents = set(ancestors.keys()) - set(dependent_counts.keys())
        else:
            have_no_dependents = ancestors.keys() - dependent_counts.keys()
        # Exit when finished or there are circular dependencies
        if not have_no_dependents:
            break
        yield have_no_dependents
        # Remove those from the ancestors
        for free_ancestor in have_no_dependents:
            for dep in ancestors[free_ancestor]:
                dependent_counts[dep] -= 1
                if dependent_counts[dep] == 0:
                    del(dependent_counts[dep])
            del(ancestors[free_ancestor])
    if ancestors:
        raise ValueError('Cyclic dependencies exist among these items: {}'.format(', '.join(
            repr(k) + ' has ' + repr(ancestors[k]) + ' depending on it'
            for k in ancestors.keys()
        )))
    yield terminators


def toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. Output is a list of
sets in topological order. The first set consists of items with no
dependences, each subsequent set consists of items that depend upon
items in the preceeding sets.
"""

    # Special case empty input.
    if len(data) == 0:
        yield set()
        raise StopIteration

    # Copy the input so as to leave it unmodified.
    data = data.copy()

    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = _reduce(set.union, data.values()) - set(data.keys())
    # Add empty dependences where needed.
    data.update(dict((item, set()) for item in extra_items_in_deps))
    while True:
        # find the next things with no (remaining) dependencies
        have_no_dependencies = set(item for item, dep in data.items() if len(dep) == 0)
        if not have_no_dependencies:
            break
        # Yield that set in one go
        yield have_no_dependencies
        # Create a new dependency graph that removes the items that have no
        # dependencies
        data = dict((item, (dep - have_no_dependencies))
                    for item, dep in data.items()
                    if item not in have_no_dependencies)
    if len(data) != 0:
        raise ValueError('Cyclic dependencies exist among these items: {}'.format(', '.join(repr(x) for x in data.items())))


def toposort_flatten_old(data, sort=True):
    """
    Returns a single list of dependencies. For any set returned by
    toposort(), those items are sorted and appended to the result (just to
    make the results deterministic).
    """

    result = []
    for d in toposort_ancestor(data):
        result.extend((sorted if sort else list)(d))
    return result


def toposort_flatten(data, sort=True):
    """
    Flatten the 'list of sets' of topologically sorted dependencies using a
    generator, optionally sorting each set of equivalent dependencies.
    """
    for dependency_group in toposort_ancestor(data):
        for dep in (sorted if sort else list)(dependency_group):
            yield dep
