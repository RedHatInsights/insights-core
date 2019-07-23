# Common Model and Query System
The `parsr.query` package allows parsers to construct data using a common
representation that can be queried with a single system.

`Entry` is the class that represents a configuration entry. It has a `name`, any
number of unnamed `attrs`, and any number of `children`. The
[httpd configuration
parser](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/httpd_conf.py)
is an example of how to construct a model using it.

## Queries
A configuration file is normally a nested structure, and it is convenient to
navigate it as if it was a set of nested dictionaries. For example, to get a top
level `IfModule` of an httpd configuration, you might do the following:

```python
ifmod = conf["IfModule"]
```

If conf was a dictionary, that would return the value of a single key. However,
conf is an `Entry`, and dictionary access executes a *query* instead of a key
lookup. The query is against all children of the current node. So the code above
actually returns a `Result` whose children are *all* entries in the top level of
conf with the name `IfModule`.

If you execute the following:

```python
cust_log = conf["IfModule"]["CustomLog"]
```

you'll get a `Result` whose children are all the entries named `CustomLog`
immediately beneath all of the top level entries named `IfModule`.

Each level of brackets represents a query against the corresponding level in the
configuration, and brackets on the left filter what's available for brackets on
the right to query against.

Queries can be more than simple values.

```python
dirs = conf["Directory", "/"]
```

The value in the first position matches against the name. Values after that
require any attribute of an entry matching the name query to be equal to them.
If multiple values come after the name, any attribute must exactly match any of
them.

This example will get all entries at the top level with a name that starts with
"Dir" and an attribute that starts with "/var/www". It shows that queries are
actually predicate objects that act on the name or attributes of configuration
entries, and simple values are translated into equality predicates for you.
```python
from parsr.query import startswith

dirs = conf[startswith("Dir"), startswith("/var/www")]
```

What if you wanted the "Options" children of all of those entries?
```python
from parsr.query import startswith

dirs = conf[startswith("Dir"), startswith("/var/www")]["Options"]
```

Remember, the first brackets query all nodes at the top level. The second
brackets query the children of those results. A third set of brackets would
query the children of *those* results, and so on.

Brackets can accept simple values, single argument predicate functions, and
predicate functions that have been "lifted" using the
[parser.query.boolean](https://github.com/csams/parsr/blob/master/parsr/query/boolean.py)
module. Lifted functions have the special property than they can be easily
combined with other lifted functions to make compound queries.

## Combining Queries
Lifted functions can be combined with logical connectives representing `and`,
`or`, and `not`. `parser.query` provides several lifted functions:

### General functions
* lt - less than
* le - less than or equal to
* eq - equality
* gt - greater than
* ge - greather than or equal to

### String functions
* contains
* startswith
* endswith

### String functions that ignore case
* ieq
* icontains
* istartswith
* iendswith

They can be connected in the following ways:
* and: `&`
* or: `|`

You can also negate:
* not: `~`

```python
# basically get virtual hosts
conf[startswith("Vir") & endswith("Host")]

# get directories or virtual hosts
conf[startswith("Dir") | startswith("VirtualHost")]

# get directories or virtual hosts
conf[eq("Directory") | eq("VirtualHost")]

# get virtual hosts with ips that start with 128 or 129.
conf["VirtualHost", startswith("128") | startswith("129")]

# get virtual hosts with ips that don't start with 128.
conf["VirtualHost", ~startswith("128")]
```

## find
Brackets work great when you know what level of the configuration you need to
look in, but what if you don't? `find` sends a query all over the configuration
looking for matches. It returns the matching leaf nodes by default.
```python
log_levels = conf.find("LogLevel")
```

Passing multiple arguments to `find` is like using a separate set of brackets.
This will find all `LogLevel` entries immediately beneath all `VirtualHost`
entries regardless of where the VirtualHost entries exist in the configuration:
```python
log_levels = conf.find("VirtualHost", "LogLevel")
```

If you want to constrain attributes in addition to names, use tuples for a given
argument position. Here, the first argument to `find` is a tuple, and the second
argument is a simple value:
```python
log_levels = conf.find(("VirtualHost", startswith("128")), "LogLevel")
```

You can also chain the `find` calls. This will find all `LogLevel` entries
anywhere beneath any `VirtualHost` entry.
```python
log_levels = conf.find("VirtualHost").find("LogLevel")
```

If you want to search for structure somewhere in the tree but are interested in
the root entries that contain the matches, pass `roots=True` to `find`.

## Lifting
To create your own predicates that can be combined using the connectors above,
use the `lift` and `lift2` functions from `parsr.query`.

`lift` is for predicates that take a single value, which will be either an entry
name or an entry attribute. `lift2` is for functions that need to be
parameterized with a value. An example of `lift2` is `operator.eq` or
`str.startswith`.

```python
def is_even(v):
    return (v % 2) == 0

def is_greater_than(a, b):
    return a > b

even = lift(is_even)
# lift allows is_even to be negated with ~ or connected to other predicates with
# & and |.

greater_than = lift2(greater_than)
# you can call greater_than in a query and pass it a single value, which will
# get substitued as the *second* parameter when it's actually applied during the
# evalutation. For example, greater_than(2) binds 2 to the parameter `b` in
# `is_greater_than`. When the attribute gets passed to `greater_than` during the
# evaluation, then its value will bind to `a`.

result = conf["server"]["port", even & greater_than(1024)]
```

`lift` and `lift2` take an optional keyword called `ignore_case` that causes all
string values to be converted to lower case before comparison.

## all_ and any_
If you need all attributes to match a query, use `all_`. If you need any
attribute to match a query, use `any_`. If you use `any_` or `all_`, it must be
the only query in the attribute position of the search. A search with multiple
queries in the attribute positions succeeds if any of the queries succeed. You
also can connect `any_` and `all_` with `&` and `|` or negate them with `~`.
```python
# all attributes must be even and greater than 15.
conf["foo", all_(even & gt(15))]

# any attribute must be even or greater than 15
conf["bar", any_(even | gt(15))]
```
