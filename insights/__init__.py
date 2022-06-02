"""
Insights Core is a data collection and analysis framework that is built for
extensibility and rapid development. It includes a set of reusable components
for gathering data in myriad ways and providing a reliable object model for it.

.. code-block: python

    >>> from insights import run
    >>> from insights.parsers import installed_rpms as rpm
    >>> lower = rpm.Rpm("bash-4.4.11-1.fc26")
    >>> upper = rpm.Rpm("bash-4.4.22-1.fc26")
    >>> results = run(rpm.Installed)
    >>> rpms = results[rpm.Installed]
    >>> rpms.newest("bash")
    "0:bash-4.4.12-7.fc26"
    >>> lower <= rpms.newest("bash") < upper
    True
"""
from __future__ import print_function
import logging
import pkgutil
import os
import sys
import yaml

from collections import defaultdict
from contextlib import contextmanager

from .core import Scannable, LogFileOutput, Parser, IniConfigFile  # noqa: F401
from .core import FileListing, LegacyItemAccess, SysconfigOptions  # noqa: F401
from .core import YAMLParser, JSONParser, XMLParser, CommandParser  # noqa: F401
from .core import AttributeDict  # noqa: F401
from .core import Syslog  # noqa: F401
from .core import taglang
from .core.archives import COMPRESSION_TYPES, extract, InvalidArchive, InvalidContentType  # noqa: F401
from .core import dr  # noqa: F401
from .core.context import ClusterArchiveContext, HostContext, HostArchiveContext, SerializedArchiveContext, ExecutionContext  # noqa: F401
from .core.dr import SkipComponent  # noqa: F401
from .core.hydration import create_context, initialize_broker  # noqa: F401
from .core.plugins import combiner, fact, metadata, parser, rule  # noqa: F401
from .core.plugins import datasource, condition, incident  # noqa: F401
from .core.plugins import make_response, make_metadata, make_fingerprint  # noqa: F401
from .core.plugins import make_pass, make_fail, make_info, make_none  # noqa: F401
from .core.filters import add_filter, apply_filters, get_filters  # noqa: F401
from .formats import get_formatter
from .parsers import get_active_lines  # noqa: F401
from .util import defaults  # noqa: F401
from .formats import Formatter as FormatterClass

from .core.spec_factory import RawFileProvider, TextFileProvider

log = logging.getLogger(__name__)


package_info = dict((k, None) for k in ["RELEASE", "COMMIT", "VERSION", "NAME"])


for name in package_info:
    package_info[name] = pkgutil.get_data(__name__, name).strip().decode("utf-8")

_COLOR = "auto"


def get_nvr():
    return "{0}-{1}-{2}".format(package_info["NAME"],
                                package_info["VERSION"],
                                package_info["RELEASE"])


@contextmanager
def get_pool(parallel, prefix, kwargs):
    """
    Yields:
        a ThreadPoolExecutor if parallel is True and `concurrent.futures` exists.
        `None` otherwise.
    """
    if parallel:
        try:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(thread_name_prefix=prefix, **kwargs) as pool:
                yield pool
        except ImportError:
            yield None
    else:
        yield None


RULES_STATUS = {}
"""
Mapping of dictionaries containing nvr and commitid for each rule repo included
in this instance

{"rule_repo_1": {"version": nvr(), "commit": sha1}}
"""


def add_status(name, nvr, commit=None):
    """
    Rule repositories should call this method in their package __init__ to
    register their version information.
    """
    RULES_STATUS[name] = {"version": nvr, "commit": commit}


add_status(package_info["NAME"], get_nvr(), package_info["COMMIT"])


def process_dir(broker, root, graph, context, inventory=None, parallel=False):
    ctx, broker = initialize_broker(root, context=context, broker=broker)
    log.debug("Processing %s with %s" % (root, ctx))

    if isinstance(ctx, ClusterArchiveContext):
        from .core.cluster import process_cluster
        archives = [f for f in ctx.all_files if f.endswith(COMPRESSION_TYPES)]
        return process_cluster(graph, archives, broker=broker, inventory=inventory)

    graph = dict((k, v) for k, v in graph.items() if k in dr.COMPONENTS[dr.GROUPS.single])
    if parallel:
        with get_pool(parallel, "insights-run-pool", {"max_workers": None}) as pool:
            broker = dr.run_all(graph, broker, pool)
    else:
        broker = dr.run(graph, broker=broker)
    return broker


def _run(broker, graph=None, root=None, context=None, inventory=None, parallel=False):
    """
    run is a general interface that is meant for stand-alone scripts to use
    when executing insights components.

    Args:
        broker (Broker): Optionally pass a broker to use for evaluation. One is
            created by default, but it's often useful to seed a broker with an
            initial dependency.
        graph (function or class): The component to execute. Will only execute
            the component and its dependency graph. If None, all components with
            met dependencies will execute.
        root (str): None will cause a host collection in which command and
            file specs are run. A directory or archive path will cause
            collection from the directory or archive, and only file type specs
            or those that depend on `insights.core.context.HostArchiveContext`
            will execute.
        context (obj): The execution context that's set.
        inventory (str): Path to inventory file.
        parallel (bool): Boolean as to weather to use parallel execution or not.

    Returns:
        broker: object containing the result of the evaluation.
    """
    if not root:
        context = context or HostContext
        broker[context] = context()
        graph = dict((k, v) for k, v in graph.items() if k in dr.COMPONENTS[dr.GROUPS.single])
        if parallel:
            with get_pool(parallel, "insights-run-pool", {"max_workers": None}) as pool:
                dr.run_all(graph, broker, pool)
        else:
            return dr.run(graph, broker=broker)

    if os.path.isdir(root):
        return process_dir(broker, root, graph, context, inventory=inventory, parallel=parallel)
    else:
        with extract(root) as ex:
            return process_dir(broker, ex.tmp_dir, graph, context, inventory=inventory, parallel=parallel)


def load_default_plugins():
    dr.load_components("insights.specs.default")
    dr.load_components("insights.specs.insights_archive")
    dr.load_components("insights.specs.core3_archive")
    dr.load_components("insights.specs.sos_archive")
    dr.load_components("insights.specs.jdr_archive")
    dr.load_components("insights.specs.must_gather_archive")


def load_packages(packages):
    plugins = []
    for name in packages:
        if name not in sys.modules:
            plugins.append(name)
            dr.load_components(name, continue_on_error=False)

    return plugins


def parse_plugins(p):
    plugins = []
    if p:
        for path in p.split(","):
            path = path.strip()
            if path.endswith(".py"):
                path, _ = os.path.splitext(path)
            path = path.rstrip("/").replace("/", ".")
            plugins.append(path)
    return plugins


def apply_default_enabled(config):
    """
    Configures dr and already loaded components with a default enabled
    value.
    """
    default_enabled = config.get("default_component_enabled", True)
    for k in dr.ENABLED:
        dr.ENABLED[k] = default_enabled

    enabled = defaultdict(lambda: default_enabled)
    enabled.update(dr.ENABLED)
    dr.ENABLED = enabled


def apply_configs(config):
    """
    Configures components.

    Args:
        config (dict): a dictionary with the following keys:
            default_component_enabled (bool, optional): default value for
                whether components are enable if not specifically declared in
                the config section. Defaults to True.

            configs (list): list of dictionaries with the following keys:
                name, enabled, metadata, and timeout. All keys are optional
                except name.

                name is the prefix or exact name of any loaded component. Any
                component starting with name will have the associated
                configuration applied.

                enabled is whether the matching components will execute even if
                their dependencies are met. Defaults to True.

                timeout sets the class level timeout attribute of any component
                so long as the attribute already exists.

                metadata is any dictionary that you want to attach to the
                component. The dictionary can be retrieved by the component at
                runtime.
    """
    default_enabled = config.get("default_component_enabled", True)
    delegate_keys = sorted(dr.DELEGATES, key=dr.get_name)
    for comp_cfg in config.get("configs", []):
        name = comp_cfg.get("name")
        for c in delegate_keys:
            delegate = dr.DELEGATES[c]
            cname = dr.get_name(c)
            if cname.startswith(name):
                dr.ENABLED[c] = comp_cfg.get("enabled", default_enabled)
                delegate.metadata.update(comp_cfg.get("metadata", {}))
                delegate.tags = set(comp_cfg.get("tags", delegate.tags))
                for k, v in delegate.metadata.items():
                    if hasattr(c, k):
                        log.debug("Setting %s.%s to %s", cname, k, v)
                        setattr(c, k, v)

                if hasattr(c, "timeout"):
                    c.timeout = comp_cfg.get("timeout", c.timeout)

                if hasattr(delegate, "links"):
                    delegate.links = comp_cfg.get("links", delegate.links)
            if cname == name:
                break


def _load_context(path):
    if path is None:
        return

    if "." not in path:
        path = ".".join(["insights.core.context", path])
    return dr.get_component(path)


def run(component=None, root=None, print_summary=False,
        context=None, inventory=None, print_component=None):

    args = None
    formatters = None

    if print_summary:
        import argparse
        import logging
        p = argparse.ArgumentParser(add_help=False)
        p.add_argument("archive", nargs="?", help="Archive or directory to analyze.")
        p.add_argument("-b", "--bare",
                       help='Specify "spec=filename[,spec=filename,...]" to use the bare file for the spec', default="")
        p.add_argument("-c", "--config", help="Configure components.")
        p.add_argument("-f", "--format", help="Output format.", default="insights.formats.text")
        p.add_argument("-i", "--inventory", help="Ansible inventory file for cluster analysis.")
        p.add_argument("-k", "--pkg-query", help="Expression to select rules by package.")
        p.add_argument("-p", "--plugins", default="",
                       help="Comma-separated list without spaces of package(s) or module(s) containing plugins.")
        p.add_argument("-s", "--syslog", help="Log results to syslog.", action="store_true")
        p.add_argument("-v", "--verbose", help="Verbose output.", action="store_true")
        p.add_argument("-D", "--debug", help="Verbose debug output.", action="store_true")
        p.add_argument("--color", default="auto", choices=["always", "auto", "never"], metavar="[=WHEN]",
                       help="Choose if and how the color encoding is outputted. When is 'always', 'auto', or 'never'.")
        p.add_argument("--context", help="Execution Context. Defaults to HostContext if an archive isn't passed.")
        p.add_argument("--no-load-default", help="Don't load the default plugins.", action="store_true")
        p.add_argument("--parallel", help="Execute rules in parallel.", action="store_true")
        p.add_argument("--tags", help="Expression to select rules by tag.")

        class Args(object):
            pass

        formatters = []
        args = Args()
        p.parse_known_args(namespace=args)
        p = argparse.ArgumentParser(parents=[p])

        if not args.no_load_default:
            load_default_plugins()

        global _COLOR
        _COLOR = args.color

        args.format = "insights.formats._json" if args.format == "json" else args.format
        args.format = "insights.formats._yaml" if args.format == "yaml" else args.format
        fmt = args.format if "." in args.format else "insights.formats." + args.format

        Formatter = dr.get_component(fmt)
        if not Formatter or not isinstance(Formatter, FormatterClass):
            dr.load_components(fmt, continue_on_error=False)
            Formatter = get_formatter(fmt)

        Formatter.configure(p)
        p.parse_args(namespace=args)
        formatter = Formatter(args)
        formatters.append(formatter)

        if args.syslog:
            fmt = "insights.formats._syslog"
            Formatter = dr.get_component(fmt)
            if not Formatter:
                dr.load_components(fmt, continue_on_error=False)
                Formatter = get_formatter(fmt)
            p.parse_args(namespace=args)
            formatter = Formatter(args)
            formatters.append(formatter)

        logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO if args.verbose else logging.ERROR)
        context = _load_context(args.context) or context
        inventory = args.inventory

        root = args.archive or root
        if root:
            root = os.path.realpath(root)

        plugins = parse_plugins(args.plugins)
        for p in plugins:
            dr.load_components(p, continue_on_error=False)

        if args.config:
            with open(args.config) as f:
                config = (yaml.safe_load(f))
                packages_loaded = load_packages(config.get('packages', []))
                plugins.extend(packages_loaded)
                apply_default_enabled(config)
                apply_configs(config)

        if component is None:
            component = []
            plugins = tuple(plugins)
            for c in dr.DELEGATES:
                if c.__module__.startswith(plugins):
                    component.append(c)

    if component:
        if not isinstance(component, (list, set)):
            component = [component]

        if args and args.pkg_query:
            pred = taglang.parse(args.pkg_query)
            component = [c for c in component if pred([dr.get_module_name(c)])]
            if not component:
                msg = "No components for pkg-query expression: %s" % args.pkg_query
                raise Exception(msg)

        if args and args.tags:
            pred = taglang.parse(args.tags)
            component = [c for c in component if pred(dr.get_tags(c))]
            if not component:
                msg = "No components for tag expression: %s" % args.tags
                raise Exception(msg)

        graph = {}
        for c in component:
            graph.update(dr.get_dependency_graph(c))
    else:
        graph = dr.COMPONENTS[dr.GROUPS.single]

    broker = dr.Broker()

    if args and args.bare:
        ctx = ExecutionContext()  # dummy context that no spec depend on. needed for filters to work
        specs = parse_specs(args.bare)
        specs = load_specs(specs, ctx)

        broker = dr.Broker()
        broker[ExecutionContext] = ctx
        for spec, content in specs.items():
            broker[spec] = content if dr.DELEGATES[spec].multi_output else content[-1]
    try:
        if formatters:
            for formatter in formatters:
                formatter.preprocess(broker)

            if args:
                if args.bare:
                    broker = dr.run(graph, broker=broker)
                else:
                    broker = _run(broker, graph, root, context=context, inventory=inventory, parallel=args.parallel)
            else:
                broker = _run(broker, graph, root, context=context, inventory=inventory)

            for formatter in formatters:
                formatter.postprocess(broker)
        elif print_component:
            if args:
                if args.bare:
                    broker = dr.run(graph, broker=broker)
                else:
                    broker = _run(broker, graph, root, context=context, inventory=inventory, parallel=args.parallel)
            else:
                broker = _run(broker, graph, root, context=context, inventory=inventory)

            broker.print_component(print_component)
        else:
            if args:
                if args.bare:
                    broker = dr.run(graph, broker=broker)
                else:
                    broker = _run(broker, graph, root, context=context, inventory=inventory, parallel=args.parallel)
            else:
                broker = _run(broker, graph, root, context=context, inventory=inventory)

        return broker
    except (InvalidContentType, InvalidArchive):
        if args and args.archive:
            path = args.archive
            msg = "Invalid directory or archive. Did you mean to pass -p {p}?"
            log.error(msg.format(p=path))
        else:
            raise


def parse_specs(specs):
    """
    -b "hostname=/etc/hostname, redhat_release=/etc/redhat-release, .."
    """
    return dict(s.strip().split("=", 1) for s in specs.split(","))


def load_datasource(name):
    name = "insights.specs.Specs." + name if "." not in name else name
    return dr.get_component(name)


def load_specs(specs, ctx):
    results = defaultdict(list)
    for spec, path in specs.items():
        s = load_datasource(spec)
        root = "/" if path.startswith('/') else "."
        if s.raw:
            c = RawFileProvider(relative_path=path, root=root, ds=s, ctx=ctx)
        else:
            c = TextFileProvider(relative_path=path, root=root, ds=s, ctx=ctx)
        results[s].append(c)
    return results


def main():
    if "" not in sys.path:
        sys.path.insert(0, "")
    run(print_summary=True)


if __name__ == "__main__":
    main()
