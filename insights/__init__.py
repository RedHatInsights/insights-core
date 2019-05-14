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

from .core import Scannable, LogFileOutput, Parser, IniConfigFile  # noqa: F401
from .core import FileListing, LegacyItemAccess, SysconfigOptions  # noqa: F401
from .core import YAMLParser, JSONParser, XMLParser, CommandParser  # noqa: F401
from .core import AttributeDict  # noqa: F401
from .core import Syslog  # noqa: F401
from .core.archives import COMPRESSION_TYPES, extract, InvalidArchive, InvalidContentType  # noqa: F401
from .core import dr  # noqa: F401
from .core.context import ClusterArchiveContext, HostContext, HostArchiveContext, SerializedArchiveContext  # noqa: F401
from .core.dr import SkipComponent  # noqa: F401
from .core.hydration import create_context
from .core.plugins import combiner, fact, metadata, parser, rule  # noqa: F401
from .core.plugins import datasource, condition, incident  # noqa: F401
from .core.plugins import make_response, make_metadata, make_fingerprint  # noqa: F401
from .core.plugins import make_pass, make_fail  # noqa: F401
from .core.filters import add_filter, apply_filters, get_filters  # noqa: F401
from .core.serde import Hydration
from .formats import get_formatter
from .parsers import get_active_lines  # noqa: F401
from .util import defaults  # noqa: F401
from .formats import Formatter as FormatterClass

log = logging.getLogger(__name__)


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


def process_dir(broker, root, graph, context, inventory=None):
    ctx = create_context(root, context)
    log.debug("Processing %s with %s" % (root, ctx))

    if isinstance(ctx, ClusterArchiveContext):
        from .core.cluster import process_cluster
        archives = [f for f in ctx.all_files if f.endswith(COMPRESSION_TYPES)]
        return process_cluster(graph, archives, broker=broker, inventory=inventory)

    broker[ctx.__class__] = ctx
    if isinstance(ctx, SerializedArchiveContext):
        h = Hydration(ctx.root)
        broker = h.hydrate(broker=broker)
    graph = dict((k, v) for k, v in graph.items() if k in dr.COMPONENTS[dr.GROUPS.single])
    broker = dr.run(graph, broker=broker)
    return broker


def _run(broker, graph=None, root=None, context=None, inventory=None):
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

    if not root:
        context = context or HostContext
        broker[context] = context()
        graph = dict((k, v) for k, v in graph.items() if k in dr.COMPONENTS[dr.GROUPS.single])
        return dr.run(graph, broker=broker)

    if os.path.isdir(root):
        return process_dir(broker, root, graph, context, inventory=inventory)
    else:
        with extract(root) as ex:
            return process_dir(broker, ex.tmp_dir, graph, context, inventory=inventory)


def load_default_plugins():
    dr.load_components("insights.specs.default")
    dr.load_components("insights.specs.insights_archive")
    dr.load_components("insights.specs.sos_archive")
    dr.load_components("insights.specs.jdr_archive")


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


def apply_default_enabled(default_enabled):
    """
    Configures dr and already loaded components with a default enabled
    value.
    """
    for k in dr.ENABLED:
        dr.ENABLED[k] = default_enabled

    enabled = defaultdict(lambda: default_enabled)
    enabled.update(dr.ENABLED)
    dr.ENABLED = enabled


def apply_configs(config):
    """
    Configures components. They can be enabled or disabled, have timeouts set
    if applicable, and have metadata customized. Valid keys are name, enabled,
    metadata, and timeout.

    Args:
        config (list): a list of dictionaries with the following keys:
            default_component_enabled (bool): default value for whether compoments
                are enable if not specifically declared in the config section

            packages (list): a list of packages to be loaded. These will be in
                addition to any packages previosly loaded for the `-p` option

            configs:
                name, enabled, metadata, and timeout. All keys are optional except
                name.

                name is the prefix or exact name of any loaded component. Any
                component starting with name will have the associated configuration
                applied.

                enabled is whether the matching components will execute even if
                their dependencies are met. Defaults to True.

                timeout sets the class level timeout attribute of any component so
                long as the attribute already exists.

                metadata is any dictionary that you want to attach to the
                component. The dictionary can be retrieved by the component at
                runtime.
    """
    default_enabled = config.get('default_component_enabled', False)
    delegate_keys = sorted(dr.DELEGATES, key=dr.get_name)
    for comp_cfg in config.get('configs', []):
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

    load_default_plugins()

    args = None
    formatter = None
    formatters = None
    if print_summary:
        import argparse
        import logging
        p = argparse.ArgumentParser(add_help=False)
        p.add_argument("archive", nargs="?", help="Archive or directory to analyze.")
        p.add_argument("-p", "--plugins", default="", help="Comma-separated list without spaces of package(s) or module(s) containing plugins.")
        p.add_argument("-c", "--config", help="Configure components.")
        p.add_argument("-i", "--inventory", help="Ansible inventory file for cluster analysis.")
        p.add_argument("-v", "--verbose", help="Verbose output.", action="store_true")
        p.add_argument("-f", "--format", help="Output format.", default="insights.formats.text")
        p.add_argument("-s", "--syslog", help="Log results to syslog.", action="store_true")
        p.add_argument("-D", "--debug", help="Verbose debug output.", action="store_true")
        p.add_argument("--context", help="Execution Context. Defaults to HostContext if an archive isn't passed.")

        class Args(object):
            pass

        formatters = []
        args = Args()
        p.parse_known_args(namespace=args)
        p = argparse.ArgumentParser(parents=[p])
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
        graph = {}
        for c in component:
            graph.update(dr.get_dependency_graph(c))
    else:
        graph = dr.COMPONENTS[dr.GROUPS.single]

    broker = dr.Broker()

    try:
        if formatters:
            for formatter in formatters:
                formatter.preprocess(broker)
            broker = _run(broker, graph, root, context=context, inventory=inventory)
            for formatter in formatters:
                formatter.postprocess(broker)
        elif print_component:
            broker = _run(broker, graph, root, context=context, inventory=inventory)
            broker.print_component(print_component)
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


def main():
    if "" not in sys.path:
        sys.path.insert(0, "")
    run(print_summary=True)


if __name__ == "__main__":
    main()
