from __future__ import print_function
import copy
import inspect
import itertools
import json
import logging
import six
import six.moves
from collections import defaultdict
from functools import wraps

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import insights
from insights import apply_filters
from insights.core import dr, filters
from insights.core.context import Context
from insights.core.spec_factory import RegistryPoint
from insights.specs import Specs


# we intercept the add_filter call during integration testing so we can ensure
# that rules add filters to datasources that *should* be filterable
ADDED_FILTERS = defaultdict(set)
add_filter = filters.add_filter


def _intercept(func):
    @wraps(func)
    def inner(ds, pattern):
        ret = add_filter(ds, pattern)
        calling_module = inspect.stack()[1][0].f_globals.get("__name__")
        ADDED_FILTERS[calling_module].add(ds)
        return ret
    return inner


filters.add_filter = _intercept(filters.add_filter)
insights.add_filter = _intercept(insights.add_filter)


def _get_registry_points(component):
    results = set()
    for c in dr.walk_tree(component):
        try:
            if isinstance(c, RegistryPoint):
                results.add(c)
        except:
            pass
    return results


logger = logging.getLogger(__name__)

ARCHIVE_GENERATORS = []
HEARTBEAT_ID = "99e26bb4823d770cc3c11437fe075d4d1a4db4c7500dad5707faed3b"
HEARTBEAT_NAME = "insights-heartbeat-9cd6f607-6b28-44ef-8481-62b0e7773614"

DEFAULT_RELEASE = "Red Hat Enterprise Linux Server release 7.2 (Maipo)"
DEFAULT_HOSTNAME = "hostname.example.com"


def unordered_compare(result, expected):
    """
    Deep compare rule reducer results when testing.  Developed to find
    arbitrarily nested lists and remove differences based on ordering.
    """
    logger.debug("--Comparing-- (%s) %s to (%s) %s", type(result), result, type(expected), expected)

    if isinstance(result, dict) and expected is None:
        assert result["type"] == "skip", result
        return

    if not all(isinstance(o, six.string_types) for o in (result, expected)):
        assert issubclass(type(result), type(expected))

    if isinstance(result, list):
        assert len(result) == len(expected)
        for left_item, right_item in six.moves.zip(sorted(result), sorted(expected)):
            unordered_compare(left_item, right_item)
    elif isinstance(result, dict):
        assert len(result) == len(expected)
        for item_key in result:
            unordered_compare(result[item_key], expected[item_key])
    else:
        assert result == expected


def run_input_data(component, input_data):
    broker = dr.Broker()
    for k, v in input_data.data.items():
        broker[k] = v

    graph = dr.get_dependency_graph(component)
    broker = dr.run(graph, broker=broker)
    for v in broker.tracebacks.values():
        print(v)
    return broker


def run_test(component, input_data, expected=None):
    if filters.ENABLED:
        mod = component.__module__
        sup_mod = '.'.join(mod.split('.')[:-1])
        rps = _get_registry_points(component)
        filterable = set(d for d in rps if dr.get_delegate(d).filterable)
        missing_filters = filterable - ADDED_FILTERS.get(mod, set()) - ADDED_FILTERS.get(sup_mod, set())
        if missing_filters:
            names = [dr.get_name(m) for m in missing_filters]
            msg = "%s must add filters to %s"
            raise Exception(msg % (mod, ", ".join(names)))

    broker = run_input_data(component, input_data)
    if expected:
        unordered_compare(broker.get(component), expected)
    return broker.get(component)


def integrate(input_data, component):
    return run_test(component, input_data)


def context_wrap(lines,
                 path="path",
                 hostname=DEFAULT_HOSTNAME,
                 release=DEFAULT_RELEASE,
                 version="-1.-1",
                 machine_id="machine_id",
                 strip=True,
                 split=True,
                 **kwargs):
    if isinstance(lines, six.string_types):
        if strip:
            lines = lines.strip()
        if split:
            lines = lines.splitlines()

    return Context(content=lines,
                   path=path, hostname=hostname,
                   release=release, version=version.split("."),
                   machine_id=machine_id, relative_path=path, **kwargs)


input_data_cache = {}


counter = itertools.count()


def create_metadata(system_id, product):
    ctx_metadata = {
        "system_id": system_id,
        "links": []
    }
    ctx_metadata["type"] = product.role
    ctx_metadata["product"] = product.__class__.__name__
    return json.dumps(ctx_metadata)


class InputData(object):
    """
    Helper class used with integrate. The role of this class is to represent
    data files sent to parsers and rules in a format similar to what lays on
    disk.

    Example Usage::

        input_data = InputData()
        input_data.add("messages", "this is some messages content")
        input_data.add("uname", "this is some uname content")

    If `release` is specified when InputData is constructed, it will be
    added to every *mock* record when added. This is useful for testing parsers
    that rely on context.release.

    If `path` is specified when calling the `add` method, the record will
    contain the specified value in the context.path field.  This is useful for
    testing pattern-like file parsers.
    """
    def __init__(self, name=None, hostname=None):
        cnt = input_data_cache.get(name, 0)
        self.name = "{0}-{1:0>5}".format(name, cnt)
        self.data = {}
        input_data_cache[name] = cnt + 1
        if hostname:
            self.add(Specs.hostname, hostname)

    def __setitem__(self, key, value):
        self.add(key, value)

    def __getitem__(self, key):
        return self.data[key]

    def _make_path(self):
        return str(next(counter)) + "BOGUS"

    def get(self, key, default):
        return self.data.get(key, default)

    def items(self):
        return self.data.items()

    def clone(self, name):
        the_clone = InputData(name)
        the_clone.data = {}
        for k, v in self.data.items():
            the_clone.data[k] = copy.deepcopy(v)
        return the_clone

    def add_component(self, comp, obj):
        """
        Allow adding arbitrary objects as components. This allows tests to mock
        components that have external dependencies so their dependents can be
        integration tested.
        """
        self.data[comp] = obj

    def add(self, spec, content, path=None, do_filter=True):
        if not path:  # path must change to allow parsers to fire
            path = self._make_path()
        if not path.startswith("/"):
            path = "/" + path

        if dr.get_delegate(spec).raw:
            content_iter = content
        else:
            if not isinstance(content, list):
                content_iter = [l.rstrip() for l in StringIO(content).readlines()]
            else:
                content_iter = content

            if do_filter:
                content_iter = list(apply_filters(spec, content_iter))

        content_provider = context_wrap(content_iter, path=path, split=False)
        if dr.get_delegate(spec).multi_output:
            if spec not in self.data:
                self.data[spec] = []
            self.data[spec].append(content_provider)
        else:
            self.data[spec] = content_provider

        return self

    def __repr__(self):
        if self.name:
            return "<InputData {name:%s}>" % (self.name)
        else:
            return super(InputData, self).__repr__()


# Helper constants when its necessary to test for a specific RHEL major version
# eg RHEL6, but the minor version isn't important
RHEL4 = "Red Hat Enterprise Linux AS release 4 (Nahant Update 9)"
RHEL5 = "Red Hat Enterprise Linux Server release 5.11 (Tikanga)"
RHEL6 = "Red Hat Enterprise Linux Server release 6.5 (Santiago)"
RHEL7 = "Red Hat Enterprise Linux Server release 7.0 (Maipo)"


def redhat_release(major, minor=""):
    """
    Helper function to construct a redhat-release string for a specific RHEL
    major and minor version.  Only constructs redhat-releases for RHEL major
    releases 4, 5, 6 & 7

    Arguments:
        major: RHEL major number. Accepts str, int or float (as major.minor)
        minor: RHEL minor number. Optional and accepts str or int

    For example, to construct a redhat-release for::

        RHEL4U9:  redhat_release('4.9') or (4.9) or (4, 9)
        RHEL5 GA: redhat_release('5')   or (5.0) or (5, 0) or (5)
        RHEL6.6:  redhat_release('6.6') or (6.6) or (6, 6)
        RHEL7.1:  redhat_release('7.1') or (7.1) or (7, 1)

    Limitation with float args: (x.10) will be parsed as minor = 1
    """
    if isinstance(major, str) and "." in major:
        major, minor = major.split(".")
    elif isinstance(major, float):
        major, minor = str(major).split(".")
    elif isinstance(major, int):
        major = str(major)
    if isinstance(minor, int):
        minor = str(minor)

    if major == "4":
        if minor:
            minor = "" if minor == "0" else " Update %s" % minor
        return "Red Hat Enterprise Linux AS release %s (Nahant%s)" % (major, minor)

    template = "Red Hat Enterprise Linux Server release %s%s (%s)"
    if major == "5":
        if minor:
            minor = "" if minor == "0" else "." + minor
        return template % (major, minor, "Tikanga")
    elif major == "6" or major == "7":
        if not minor:
            minor = "0"
        name = "Santiago" if major == "6" else "Maipo"
        return template % (major, "." + minor, name)
    else:
        raise Exception("invalid major version: %s" % major)


def archive_provider(component, test_func=unordered_compare, stride=1):
    """
    Decorator used to register generator functions that yield InputData and
    expected response tuples.  These generators will be consumed by py.test
    such that:

    - Each InputData will be passed into an integrate() function
    - The result will be compared [1] against the expected value from the
      tuple.

    Parameters
    ----------
    component: (str)
        The component to be tested.
    test_func: function
        A custom comparison function with the parameters (result, expected).
        This will override the use of the compare() [1] function.
    stride: int
        yield every `stride` InputData object rather than the full set. This
        is used to provide a faster execution path in some test setups.

    [1] insights.tests.unordered_compare()
    """
    def _wrap(func):
        @six.wraps(func)
        def __wrap(stride=stride):
            for input_data, expected in itertools.islice(func(), None, None, stride):
                yield component, test_func, input_data, expected

        __wrap.stride = stride
        ARCHIVE_GENERATORS.append(__wrap)
        return __wrap
    return _wrap
