import copy
import itertools
import logging
import pprint
import json
import sys
import tempfile
from collections import defaultdict
from functools import wraps
from itertools import islice
from insights.core import mapper, reducer, marshalling, plugins
from insights.core.context import Context, PRODUCT_NAMES
from insights.util import make_iter


logger = logging.getLogger("test.util")

ARCHIVE_GENERATORS = []
HEARTBEAT_ID = "99e26bb4823d770cc3c11437fe075d4d1a4db4c7500dad5707faed3b"
HEARTBEAT_NAME = "insights-heartbeat-9cd6f607-6b28-44ef-8481-62b0e7773614"


def insights_heartbeat(metadata={"product_code": "rhel", "role": "host"}):
    # Do the import in this function so that the archive tool project isn't
    # pulled in unless you're running this project's unit tests.

    # Need to alias the name of TestArchive since pytest looks at it becuase it
    # starts with "Test".
    from insights_archive.tool import TestArchive as TA, Transform as T
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


def archive_provider(module, test_func=unordered_compare, stride=1):
    """
    Decorator used to register generator functions that yield InputData and
    expected response tuples.  These generators will be consumed by py.test
    such that:

    - Each InputData will be passed into an integrate() function
    - The result will be compared [1] against the expected value from the
      tuple.

    Parameters
    ----------
    module: (str)
        The module to be tested.
    test_func: function
        A custom comparison function with the parameters
        (result, expected).  This will override the use of the compare() [1]
        function.
    stride: int
        yield every `stride` InputData object rather than the full set. This
        is used to provide a faster execution path in some test setups.

    [1] insights.rules.tests.util.compare()
    """
    def _wrap(func):
        @wraps(func)
        def __wrap(stride=stride):
            for input_data, expected in islice(func(), None, None, stride):
                yield module, test_func, input_data, expected

        __wrap.serializable_id = "#".join([func.__module__, func.__name__])
        __wrap.stride = stride
        ARCHIVE_GENERATORS.append(__wrap)
        return __wrap
    return _wrap


CACHED_BY_MODULE = defaultdict(list)


def ensure_cache_populated():
    if not CACHED_BY_MODULE:
        for gen in ARCHIVE_GENERATORS:
            for module, test_func, input_data, expected in gen():
                CACHED_BY_MODULE[module].append((test_func, input_data, expected))


def plugin_tests(module_name):
    ensure_cache_populated()
    if module_name in sys.modules:
        real_module = sys.modules[module_name]
        for test_func, input_data, expected in CACHED_BY_MODULE[real_module]:
            yield test_func, input_data, expected


def context_wrap(lines, path='path', hostname='hostname',
                 release='release', version='-1.-1', machine_id="machine_id", **kwargs):
    if isinstance(lines, basestring):
        lines = lines.strip().splitlines()

    return Context(content=lines,
                   path=path, hostname=hostname,
                   release=release, version=version.split('.'),
                   machine_id=machine_id, **kwargs)


def construct_lines(package):
    return [
        "Linewhichwillnotbesplit!",
        "xz-libs-4.999.9-0.3.beta.20091007git.el6.x86_64             Thu 22 Aug 2013 03:59:09 PM HKT",
        "{0}                                 Thu 22 Aug 2013 03:59:09 PM HKT".format(package),
        "rootfiles-8.1-6.1.el6.noarch                                Thu 22 Aug 2013 04:01:12 PM HKT"
    ]


def prep_for_reducer(list_, use_value_list=False):
    return marshalling.unmarshal_to_context(marshalling.marshal(o, use_value_list=use_value_list) for o in list_)


def get_mappers_for(module):
    for m in set(itertools.chain(plugins.PLUGINS[module.__name__]["mappers"],
                                 plugins.SHARED_MAPPERS)):
        for symbolic_name in m.symbolic_names:
            yield symbolic_name, m


def get_reducer_for(module):
    module_name = module.__name__.rpartition(".")[-1]
    f = plugins.REDUCERS.get(module_name, plugins.CLUSTER_REDUCERS.get(module_name))
    if f:
        return {module_name: f}
    else:
        return {}


def integrator(module):
    """
    Curries the integrate method with the given module. Useful for when you
    will be making multiple calls to integrate and want to dry those calls up.
    """
    return lambda input_data: integrate(input_data, module)


def integrator_assert(module):
    def _test(input_data, expected):
        result = integrate(input_data, module)
        print "Actual:"
        pprint.pprint(result)
        print "\nExpected:"
        pprint.pprint(expected)
        assert result == expected
    _test.module = module
    return _test


def error_handler(func, e, local, shared):
    logger.exception("Error in running test")


def integrate(input_data, module):
    """
    This method drives the mapreduce framework with test `input_data`.

    :param InputData input_data: InputData object filled with test data
    :param module module: module containing mappers and reducers to test with

    mappers and reducers registered by `module` are isolated and passed data
    from the `input_data` parameter. The function returns a list of reducer
    results. In most cases this will be a list of length 1.
    """
    mapper_map = defaultdict(list)
    for target, f in get_mappers_for(module):
        mapper_map[target].append(f)

    records = []
    if isinstance(input_data, InputData):
        input_data = [input_data]
        is_multi_node = False
    elif isinstance(input_data, list):
        is_multi_node = True
        if isinstance(input_data[0], dict):
            # Assume it's metadata.json
            if "systems" not in input_data[0]:
                # The multinode mappers use the presence of the "system" key to
                # validate this really is a multinode metadata.json
                input_data[0]["systems"] = []
            records.append({
                "content": json.dumps(input_data[0]),
                "release": "default-release",
                "version": ["-1", "-1"],
                "attachment_uuid": None,
                "target": "metadata.json",
                "path": "metadata.json",
                "hostname": None,
                "case_number": ""
            })
            input_data = input_data[1:]
    else:
        raise TypeError("Unrecognized test data: %s" % type(input_data))

    for in_d in input_data:
        for record in in_d.records:
            ctx = record["context"]
            new_rec = {
                "content": ctx.content,
                "release": ctx.release,
                "version": ctx.version,
                "path": ctx.path,
                "hostname": ctx.hostname,
                "attachment_uuid": ctx.machine_id,
                "target": record["target"],
                "accountnumber": record["accountnumber"],
                "case_number": ""
            }
            new_rec.update({k: v for k, v in in_d.extra_context.items() if k in PRODUCT_NAMES})
            records.append(new_rec)

    _, mapper_output = mapper.run(iter(records), mappers=mapper_map)
    reducers = get_reducer_for(module)

    if is_multi_node:
        shared_reducers = {}
        for r in reducers.values():
            requires = plugins.COMPONENT_DEPENDENCIES[r]
            shared_reducers = {i: i for i in requires if i.shared and i._reducer}
        if shared_reducers:
            for k, v in mapper_output.iteritems():
                list(reducer.run_host(v, {}, error_handler, reducers=shared_reducers))
        gen = reducer.run_multi(mapper_output, {}, error_handler, reducers=reducers)
        return [result for func, result in gen if result["type"] != "skip"]
    else:
        host_outputs = mapper_output.values()
        if len(host_outputs) == 0:
            return []
        else:
            single_host = host_outputs[0]
        assert all(not r.cluster for r in reducers.values()), "Cluster reducers not allowed in single node test"
        if not reducers:
            # Assume we're expecting a mapper to make_response.
            return [v[0] for v in single_host.values() if isinstance(v[0], dict) and "error_key" in v[0]]
        gen = reducer.run_host(single_host, {}, error_handler, reducers=reducers)
        reducer_modules = [r.__module__ for r in reducers.values()]
        return [r for func, r in gen if func.__module__ in reducer_modules and r["type"] != "skip"]


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
    data files sent to mappers and reducers in a format similar to what lays on
    disk.

    Example Usage::

        input_data = InputData()
        input_data.add("messages", "this is some messages content")
        input_data.add("uname", "this is some uname content")

    If `release` is specified when InputData is constructed, it will be
    added to every *mock* record when added. This is useful for testing mappers
    that rely on context.release.

    If `path` is specified when calling the `add` method, the record will
    contain the specified value in the context.path field.  This is useful for
    testing pattern-like file mappers.
    """

    def __init__(self, name=None, release=None, version=["-1", "-1"], hostname=None, machine_id=None, **kwargs):
        cnt = input_data_cache.get(name, 0)
        self.name = "{0}-{1:0>5}".format(name, cnt)
        input_data_cache[name] = cnt + 1
        self.records = []
        self.to_remove = []
        self.release = release if release else "default-release"
        self.version = version.split(".") if "." in version else version
        if len(self.version) == 1:
            self.version = [self.version[0], '0']
        self.machine_id = machine_id if machine_id else "input-data-" + str(next_gn())
        self.extra_context = kwargs

        # InputData.hostname (as well as Context.hostname) is now used for
        # unique identification of hosts in multi-host mode.
        # TODO: Rename field to better represent its real function
        self.hostname = self.machine_id
        self.add("hostname", hostname if hostname else "hostname.example.com")
        self.add_legacy_product_records()

    def add_legacy_product_records(self):
        ctx_metadata = {
            "system_id": self.hostname,
            "links": []
        }
        if self.extra_context.get("osp"):
            ctx_metadata["type"] = self.extra_context["osp"].role
            ctx_metadata["product"] = "OSP"
            self.add("metadata.json", json.dumps(ctx_metadata))
        elif self.extra_context.get("rhev"):
            ctx_metadata["type"] = self.extra_context["rhev"].role
            ctx_metadata["product"] = "RHEV"
            self.add("metadata.json", json.dumps(ctx_metadata))
        elif self.extra_context.get("docker"):
            ctx_metadata["type"] = self.extra_context["docker"].role
            ctx_metadata["product"] = "Docker"
            self.add("metadata.json", json.dumps(ctx_metadata))

    def get_context(self):
        return self.records[0]["context"] if len(self.records) > 0 else None

    def clone(self, name):
        the_clone = copy.deepcopy(self)
        the_clone.name = name
        return the_clone

    def add(self, target, content, path=None, do_filter=True):
        if not path:  # path must change to allow mappers to fire
            path = str(next_gn()) + "BOGUS"
        if do_filter:
            content_iter = mapper.filter_lines(make_iter(content), target)
        else:
            content_iter = make_iter(content)
        ctx = Context(content="\n".join(content_iter),
                      release=self.release,
                      version=self.version,
                      path=path,
                      hostname=self.hostname,
                      machine_id=self.machine_id,
                      **self.extra_context)

        self.records.append({
            "target": target,
            "accountnumber": "123456",
            "case_number": "",
            "attachment_uuid": self.hostname,
            "createddate": "01-01-9999",
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
    if isinstance(major, str) and '.' in major:
        major, minor = major.split('.')
    elif isinstance(major, float):
        major, minor = str(major).split('.')
    elif isinstance(major, int):
        major = str(major)
    if isinstance(minor, int):
        minor = str(minor)

    if major == '4':
        if minor:
            minor = "" if minor == '0' else " Update %s" % minor
        return "Red Hat Enterprise Linux AS release %s (Nahant%s)" % (major, minor)

    template = "Red Hat Enterprise Linux Server release %s%s (%s)"
    if major == '5':
        if minor:
            minor = "" if minor == '0' else "." + minor
        return template % (major, minor, "Tikanga")
    elif major == '6' or major == '7':
        if not minor:
            minor = "0"
        name = "Santiago" if major == '6' else "Maipo"
        return template % (major, "." + minor, name)
    else:
        raise Exception("invalid major version: %s" % major)
