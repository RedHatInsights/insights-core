import copy
import itertools
import logging
import pprint
import json
import tempfile
from collections import defaultdict
from functools import wraps
from itertools import islice

import insights
import insights.core.fava  # noqa: F401
import insights.specs_default  # noqa: F401
from insights import apply_filters, get_config

# Need to alias the name of TestArchive since pytest looks at it because it
# starts with "Test".
from insights.archive.tool import TestArchive as TA, Transform as T
from insights.core.context import Context
from insights.core.evaluators import MultiEvaluator, SingleEvaluator
from insights.core.evaluators import broker_from_spec_mapper
from insights.util import make_iter


logger = logging.getLogger(__name__)

ARCHIVE_GENERATORS = []
HEARTBEAT_ID = "99e26bb4823d770cc3c11437fe075d4d1a4db4c7500dad5707faed3b"
HEARTBEAT_NAME = "insights-heartbeat-9cd6f607-6b28-44ef-8481-62b0e7773614"

DEFAULT_RELEASE = "Red Hat Enterprise Linux Server release 7.2 (Maipo)"
DEFAULT_HOSTNAME = "hostname.example.com"


def insights_heartbeat(metadata={"product_code": "rhel", "role": "host"}):
    tmp_dir = tempfile.mkdtemp()
    hostname = HEARTBEAT_NAME
    return TA(hostname, base_archive="rhel7", transforms=[
        T("hostname").replace(hostname),
        T("metadata.json").replace(json.dumps(metadata))
    ], machine_id=HEARTBEAT_ID, hostname=hostname).build(tmp_dir)


def unordered_compare(result, expected):
    """
    Deep compare rule reducer results when testing.  Developed to find
    arbitrarily nested lists and remove differences based on ordering.
    """
    logger.debug("--Comparing-- (%s) %s to (%s) %s", type(result), result, type(expected), expected)

    if not (type(result) in [unicode, str] and type(expected) in [unicode, str]):
        assert type(result) == type(expected)

    if isinstance(result, list):
        assert len(result) == len(expected)
        for left_item, right_item in itertools.izip(sorted(result), sorted(expected)):
            unordered_compare(left_item, right_item)
    elif isinstance(result, dict):
        assert len(result) == len(expected)
        for item_key in result:
            unordered_compare(result[item_key], expected[item_key])
    else:
        assert result == expected


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
        @wraps(func)
        def __wrap(stride=stride):
            for input_data, expected in islice(func(), None, None, stride):
                yield component, test_func, input_data, expected

        __wrap.stride = stride
        ARCHIVE_GENERATORS.append(__wrap)
        return __wrap
    return _wrap


CACHED_BY_MODULE = defaultdict(list)


def ensure_cache_populated():
    if not CACHED_BY_MODULE:
        for gen in ARCHIVE_GENERATORS:
            for component, test_func, input_data, expected in gen():
                CACHED_BY_MODULE[component].append((test_func, input_data, expected))


def plugin_tests(component):
    ensure_cache_populated()
    for test_func, input_data, expected in CACHED_BY_MODULE[component]:
        yield test_func, input_data, expected


def context_wrap(lines,
                 path="path",
                 hostname=DEFAULT_HOSTNAME,
                 release=DEFAULT_RELEASE,
                 version="-1.-1",
                 machine_id="machine_id",
                 **kwargs):
    if isinstance(lines, basestring):
        lines = lines.strip().splitlines()
    return Context(content=lines,
                   path=path, hostname=hostname,
                   release=release, version=version.split("."),
                   machine_id=machine_id, **kwargs)


def integrator(component):
    """
    Curries the integrate method with the given component. Useful for when you
    will be making multiple calls to integrate and want to dry those calls up.
    """
    return lambda input_data: integrate(input_data, component)


def integrator_assert(component):
    def _test(input_data, expected):
        result = integrate(input_data, component)
        print "Actual:"
        pprint.pprint(result)
        print "\nExpected:"
        pprint.pprint(expected)
        assert result == expected
    _test.component = component
    return _test


class MultinodeShim(object):
    def __init__(self, input_datas):
        self.input_datas = input_datas

    def sub_spec_mappers(self):
        return self.input_datas

    def get_content(self, path, default=None, **kwargs):
        raise NotImplementedError()


def integrate(input_data, component):
    """
    :param InputData input_data: InputData object filled with test data
    :param callable component: component to test
    """
    if isinstance(input_data, InputData):
        b = broker_from_spec_mapper(input_data)
        evaluator = SingleEvaluator(input_data, broker=b)
        evaluator.process()
        result = evaluator.broker.instances.get(component)
        return [result] if result else []
    if isinstance(input_data, list):
        if isinstance(input_data[0], dict):
            # Assume it's metadata.json
            if "systems" not in input_data[0]:
                # The multinode parsers use the presence of the "system" key to
                # validate this really is a multinode metadata.json
                input_data[0]["systems"] = []
            meta = input_data[0]
            input_data = input_data[1:]
            evaluator = MultiEvaluator(MultinodeShim(input_data), metadata=meta)
        else:
            evaluator = MultiEvaluator(MultinodeShim(input_data))
        evaluator.process()
        result = evaluator.broker.instances.get(component)
        return [result] if result else []
    else:
        raise TypeError("Unrecognized test data: %s" % type(input_data))


input_data_cache = {}


# UUID is kinda slow
GLOBAL_NUMBER = 0


def next_gn():
    global GLOBAL_NUMBER
    GLOBAL_NUMBER += 1
    return GLOBAL_NUMBER


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
    def __init__(self, name=None,
                 release=DEFAULT_RELEASE,
                 version=["-1", "-1"],
                 hostname=DEFAULT_HOSTNAME,
                 machine_id=None,
                 **kwargs):
        cnt = input_data_cache.get(name, 0)
        self.name = "{0}-{1:0>5}".format(name, cnt)
        input_data_cache[name] = cnt + 1
        self.root = None
        self.records = []
        self.symbolic_files = defaultdict(list)
        self.data_spec_config = get_config()
        self.by_path = dict()
        self.to_remove = []
        self.release = release
        self.version = version.split(".") if "." in version else version
        if len(self.version) == 1:
            self.version = [self.version[0], "0"]
        self.machine_id = machine_id or "input-data-" + str(next_gn())
        self.extra_context = kwargs

        # InputData.hostname (as well as Context.hostname) is now used for
        # unique identification of hosts in multi-host mode.
        # TODO: Rename field to better represent its real function
        self.hostname = self.machine_id
        self.add("hostname", hostname)
        self.add("machine-id", machine_id)
        self.add("redhat-release", self.release)

    def get_context(self):
        return self.records[0]["context"] if len(self.records) > 0 else None

    def get_content(self, target, split=True, symbolic=True, default=""):
        try:
            if symbolic:
                content = self.by_path[self.symbolic_files[target][0]]
            else:
                content = self.by_path[target]
            return content.splitlines() if split else content
        except:
            return default

    def clone(self, name):
        the_clone = copy.deepcopy(self)
        the_clone.name = name
        return the_clone

    def add(self, target, content, path=None, do_filter=True):
        if not path:  # path must change to allow parsers to fire
            path = str(next_gn()) + "BOGUS"
        if not path.startswith("/"):
            path = "/" + path
        if do_filter:
            content_iter = apply_filters(target, make_iter(content))
        else:
            content_iter = make_iter(content)
        ctx = Context(target=target,
                      content="\n".join(content_iter),
                      release=self.release,
                      version=self.version,
                      path=path,
                      hostname=self.hostname,
                      machine_id=self.machine_id,
                      **self.extra_context)

        self.by_path[path] = content
        self.symbolic_files[target].append(path)

        self.records.append({
            "target": target,
            "context": ctx
        })
        return self

    def remove(self, target):
        self.to_remove.append(target)
        return self

    def __repr__(self):
        if self.name:
            return "<InputData {name:%s hostname:%s}>" % (self.name, self.hostname)
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
