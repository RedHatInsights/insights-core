from __future__ import print_function
import os
import pkgutil
from pprint import pprint
from .core import Scannable, LogFileOutput, Parser, IniConfigFile  # noqa: F401
from .core import FileListing, LegacyItemAccess, SysconfigOptions  # noqa: F401
from .core import YAMLParser, JSONParser, XMLParser, CommandParser  # noqa: F401
from .core import AttributeDict  # noqa: F401
from .core import Syslog  # noqa: F401
from .core.archives import COMPRESSION_TYPES, extract  # noqa: F401
from .core import dr  # noqa: F401
from .core.cluster import process_cluster
from .core.context import ClusterArchiveContext, HostContext, HostArchiveContext  # noqa: F401
from .core.dr import SkipComponent  # noqa: F401
from .core.hydration import create_context
from .core.plugins import combiner, fact, metadata, parser, rule  # noqa: F401
from .core.plugins import datasource, condition, incident  # noqa: F401
from .core.plugins import make_response, make_metadata, make_fingerprint  # noqa: F401
from .core.filters import add_filter, apply_filters, get_filters  # noqa: F401
from .parsers import get_active_lines  # noqa: F401
from .util import defaults  # noqa: F401


package_info = dict((k, None) for k in ["RELEASE", "COMMIT", "VERSION", "NAME"])


for name in package_info:
    package_info[name] = pkgutil.get_data(__name__, name).strip().decode("utf-8")


def get_nvr():
    return "{0}-{1}-{2}".format(package_info["NAME"],
                                package_info["VERSION"],
                                package_info["RELEASE"])


RULES_STATUS = {}
"""
Mapping of dictionaries containing nvr and commitid for each rule repo included
in this instance

{"rule_repo_1": {"version": nvr(), "commit": sha1}}
"""


def add_status(name, nvr, commit):
    """
    Rule repositories should call this method in their package __init__ to
    register their version information.
    """
    RULES_STATUS[name] = {"version": nvr, "commit": commit}


def _run(graph=None, root=None, run_context=HostContext,
         archive_context=None, show_dropped=False, use_pandas=False):
    """
    run is a general interface that is meant for stand alone scripts to use
    when executing insights components.

    Args:
        root (str): None will causes a host collection in which command and
            file specs are run. A directory or archive path will cause
            collection from the directory or archive, and only file type specs
            or those that depend on `insights.core.context.HostArchiveContext`
            will execute.
        component (function or class): The component to execute. Will only execute
            the component and its dependency graph. If None, all components with
            met dependencies will execute.

    Returns:
        broker: object containing the result of the evaluation.
    """
    broker = dr.Broker()

    if not root:
        broker[run_context] = run_context()
        return dr.run(graph, broker=broker)

    if os.path.isdir(root):
        ctx = create_context(root, archive_context)

        if isinstance(ctx, ClusterArchiveContext):
            archives = [f for f in ctx.all_files if f.endswith(COMPRESSION_TYPES)]
            return process_cluster(archives, use_pandas=use_pandas)

        broker[ctx.__class__] = ctx
        return dr.run(graph, broker=broker)

    with extract(root) as ex:
        ctx = create_context(ex.tmp_dir, archive_context)
        archive_context = ctx.__class__
        broker = dr.Broker()
        broker[archive_context] = ctx
        result = dr.run(graph, broker=broker)
        if not show_dropped:
            return result

        ds = broker.get_by_type(datasource)
        vals = []
        for v in ds.values():
            if isinstance(v, list):
                vals.extend(d.path for d in v)
            else:
                vals.append(v.path)
        dropped = set(ctx.all_files) - set(vals)
        pprint("Dropped Files:")
        pprint(dropped, indent=4)
        return result


def _load_context(path):
    if path is None:
        return

    if "." not in path:
        path = ".".join(["insights.core.context", path])
    return dr.get_component(path)


def describe(broker, show_missing=False, show_tracebacks=False):
    if show_missing and broker.missing_requirements:
        print()
        print("Missing Requirements:")
        if broker.missing_requirements:
            print(broker.missing_requirements)

    if show_tracebacks and broker.tracebacks:
        print()
        print("Tracebacks:")
        for t in broker.tracebacks.values():
            print(t)

    def printit(c, v):
        name = dr.get_name(c)
        print(name)
        print('-' * len(name))
        print(dr.to_str(c, v))
        print()
        print()

    print()
    for c in sorted(broker.get_by_type(rule), key=dr.get_name):
        v = broker[c]
        if v["type"] != "skip":
            printit(c, v)


def run(component=None, root=None, print_summary=False,
        run_context=HostContext, archive_context=None, use_pandas=False,
        print_component=None):

    from .core import dr
    dr.load_components("insights.specs.default")
    dr.load_components("insights.specs.insights_archive")
    dr.load_components("insights.specs.sos_archive")

    args = None
    if print_summary:
        import argparse
        import logging
        p = argparse.ArgumentParser()
        p.add_argument("archive", nargs="?", help="Archive or directory to analyze")
        p.add_argument("-p", "--plugins", default=[], nargs="*",
                       help="package(s) or module(s) containing plugins to run.")
        p.add_argument("-v", "--verbose", help="Verbose output.", action="store_true")
        p.add_argument("-q", "--quiet", help="Error output only.", action="store_true")
        p.add_argument("-m", "--missing", help="Show missing requirements.", action="store_true")
        p.add_argument("-t", "--tracebacks", help="Show stack traces.", action="store_true")
        p.add_argument("-d", "--dropped", help="Show collected files that weren't processed.", action="store_true", default=False)
        p.add_argument("--pandas", action="store_true", help="Use pandas dataframes with cluster rules")
        p.add_argument("--rc", help="Run Context")
        p.add_argument("--ac", help="Archive Context")
        args = p.parse_args()

        logging.basicConfig(level=logging.DEBUG if args.verbose else logging.ERROR if args.quiet else logging.INFO)
        run_context = _load_context(args.rc) or run_context
        archive_context = _load_context(args.ac) or archive_context
        use_pandas = args.pandas or use_pandas

        root = args.archive or root
        if root:
            root = os.path.realpath(root)

        for path in args.plugins:
            dr.load_components(path)

        if component is None:
            component = []
            plugins = tuple(args.plugins)
            for c in dr.DELEGATES:
                if c.__module__.startswith(plugins):
                    component.append(c)

    show_dropped = args.dropped if args else False
    if component:
        if not isinstance(component, (list, set)):
            component = [component]
        graph = {}
        for c in component:
            graph.update(dr.get_dependency_graph(c))
    else:
        graph = dr.COMPONENTS[dr.GROUPS.single]

    broker = _run(graph, root, run_context=run_context, archive_context=archive_context, show_dropped=show_dropped, use_pandas=use_pandas)

    if print_summary:
        describe(broker, show_missing=args.missing, show_tracebacks=args.tracebacks)
    elif print_component:
        broker.print_component(print_component)
    return broker


if __name__ == "__main__":
    run(print_summary=True)
