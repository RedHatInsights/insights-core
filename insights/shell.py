# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import logging
import importlib
import inspect
import os
import re
import six
import traceback
import yaml

from collections import defaultdict
from contextlib import contextmanager

import IPython
from pygments.console import ansiformat
from traitlets.config.loader import Config

from insights.core.context import SerializedArchiveContext
from insights.core.serde import Hydration
from insights.parsr.query import *  # noqa
from insights.parsr.query import eq, matches, make_child_query as q  # noqa
from insights.parsr.query.boolean import FALSE, TRUE

from insights import (
    apply_configs,
    apply_default_enabled,
    create_context,
    datasource,
    dr,
    extract,
    load_default_plugins,
    load_packages,
    parse_plugins,
)
from insights.core import plugins
from insights.core.context import HostContext
from insights.core.spec_factory import ContentProvider, RegistryPoint
from insights.formats import render
from insights.formats.text import render_links

Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

RULE_COLORS = {"fail": "brightred", "pass": "blue", "info": "magenta", "skip": "yellow"}


@contextmanager
def _create_new_broker(path=None):
    """
    Create a broker and populate it by evaluating the path with all
    registered datasources.

    Args:
        path (str): path to the archive or directory to analyze. ``None`` will
            analyze the current system.
    """
    datasources = dr.get_components_of_type(datasource)

    def make_broker(ctx):
        broker = dr.Broker()
        broker[ctx.__class__] = ctx

        if isinstance(ctx, SerializedArchiveContext):
            h = Hydration(ctx.root)
            broker = h.hydrate(broker=broker)

        dr.run(datasources, broker=broker)

        del broker[ctx.__class__]
        return broker

    if path:
        if os.path.isdir(path):
            ctx = create_context(path)
            yield (path, make_broker(ctx))
        else:
            with extract(path) as e:
                ctx = create_context(e.tmp_dir)
                yield (e.tmp_dir, make_broker(ctx))
    else:
        yield (os.curdir, make_broker(HostContext()))


# contextlib.ExitStack isn't available in all python versions
# so recurse to victory.
def with_brokers(archives, callback):
    brokers = []

    def inner(paths):
        if paths:
            path = paths.pop()
            with _create_new_broker(path) as ctx:
                brokers.append(ctx)
                inner(paths)
        else:
            callback(brokers)

    if archives:
        inner(list(reversed(archives)))
    else:
        with _create_new_broker() as ctx:
            callback([ctx])


def _get_available_models(broker, group=dr.GROUPS.single):
    """
    Given a broker populated with datasources, return everything that could
    run based on them.
    """
    state = set(broker.instances.keys())
    models = {}

    for comp in dr.run_order(dr.COMPONENTS[group]):
        if comp in dr.DELEGATES and not plugins.is_datasource(comp):
            if dr.DELEGATES[comp].get_missing_dependencies(state):
                continue

            if plugins.is_type(
                comp, (plugins.rule, plugins.condition, plugins.incident)
            ):
                name = "_".join(
                    [dr.get_base_module_name(comp), dr.get_simple_name(comp)]
                )
            else:
                name = dr.get_simple_name(comp)

            if name in models:
                prev = models[name]
                models[dr.get_name(prev).replace(".", "_")] = prev

                del models[name]
                name = dr.get_name(comp).replace(".", "_")

            models[name] = comp
            state.add(comp)

    return models


class Models(dict):
    u"""
    Represents all components that may be available given the data being
    analyzed. Use models.find() to see them. Tab complete attributes to access
    them. Use help(models) for more info.

    Start the shell with the environment variable
    INSIGHTS_FILTERS_ENABLED=False to disable filtering that may cause
    unexpected missing data.

    Examples:

        >>> models.find("rpm")
        InstalledRpms (insights.parsers.installed_rpms.InstalledRpms)

        >>> rpms = models.InstalledRpms
        >>> rpms.newest("bash")
        0:bash-4.1.2-48.el6

        >>> models.find("(?i)yum")  # Prefix "(?i)" ignores case.
        YumConf (insights.parsers.yum_conf.YumConf, parser)
        YumLog (insights.parsers.yumlog.YumLog, parser)
        YumRepoList (insights.parsers.yum.YumRepoList, parser)
        └╌╌Incorrect line: 'repolist: 33296'
        YumReposD (insights.parsers.yum_repos_d.YumReposD, parser)

        >>> models.show_trees("rpm")
        insights.parsers.installed_rpms.InstalledRpms (parser)
        ┊   insights.specs.Specs.installed_rpms (unfiltered / lines)
        ┊   ┊╌╌╌╌╌TextFileProvider("'/home/csams/Downloads/archives/sosreport-example-20191225000000/sos_commands/rpm/package-data'")
        ┊   ┊   insights.specs.insights_archive.InsightsArchiveSpecs.installed_rpms (unfiltered / lines)
        ┊   ┊   ┊   insights.specs.insights_archive.InsightsArchiveSpecs.all_installed_rpms (unfiltered / lines)
        ┊   ┊   ┊   ┊   insights.core.context.HostArchiveContext ()
        ┊   ┊   insights.specs.sos_archive.SosSpecs.installed_rpms (unfiltered / lines)
        ┊   ┊   ┊╌╌╌╌╌TextFileProvider("'/home/csams/Downloads/archives/sosreport-example-20191225000000/sos_commands/rpm/package-data'")
        ┊   ┊   ┊   insights.core.context.SosArchiveContext ()
        ┊   ┊   insights.specs.default.DefaultSpecs.installed_rpms (unfiltered / lines)
        ┊   ┊   ┊   insights.specs.default.DefaultSpecs.docker_installed_rpms (unfiltered / lines)
        ┊   ┊   ┊   ┊   insights.core.context.DockerImageContext ()
        ┊   ┊   ┊   insights.specs.default.DefaultSpecs.host_installed_rpms (unfiltered / lines)
        ┊   ┊   ┊   ┊   insights.core.context.HostContext ()
    """

    def __init__(self, broker, models, cwd, tmp, cov):
        self._requested = set()
        self._broker = broker
        self._cwd = cwd
        self._tmp = tmp
        self._cov = cov
        super(Models, self).__init__(models)

    def __dir__(self):
        """ Enabled ipython autocomplete. """
        return sorted(set(list(self.keys()) + dir(Models)))

    def _ipython_key_completions_(self):
        """ For autocomplete of keys when accessing models as a dict. """
        return sorted(self.keys())

    def __str__(self):
        return "{} components possibly available".format(len(self))

    def _get_color(self, comp):
        if comp in self._broker:
            if plugins.is_type(comp, plugins.rule) and self._broker[comp].get("type") == "skip":
                return "yellow"
            return "green"
        elif comp in self._broker.exceptions:
            return "brightred"
        elif comp in self._broker.missing_requirements:
            return "yellow"
        else:
            return ""

    def _dump_diagnostics(self, comp):
        results = []
        results.append("Dependency Tree")
        results.append("===============")
        results.extend(self._show_tree(comp))
        results.append("")
        results.append("Missing Dependencies")
        results.append("====================")
        results.extend(self._show_missing(comp))
        results.append("")
        results.append("Exceptions")
        results.append("==========")
        results.extend(self._show_exceptions(comp))
        IPython.core.page.page(six.u(os.linesep.join(results)))

    def evaluate_all(self, match=None, ignore="spec"):
        """
        Evaluate all components that match.

        Args:
            match (str, optional): regular expression for matching against
                the fully qualified name of components to keep.
            ignore (str, optional): regular expression for searching against
                the fully qualified name of components to ignore.
        """
        match, ignore = self._desugar_match_ignore(match, ignore)

        tasks = []
        for c in self.values():
            name = dr.get_name(c)
            if match.test(name) and not ignore.test(name):
                if not any(
                    [
                        c in self._broker.instances,
                        c in self._broker.exceptions,
                        c in self._broker.missing_requirements,
                    ]
                ):
                    tasks.append(c)

        if not tasks:
            return

        dr.run(tasks, broker=self._broker)
        self.show_timings(match, ignore)

    def evaluate(self, name):
        """
        Evaluate a component and return its result. Prints diagnostic
        information in the case of failure. This function is useful when a
        component's name contains characters that aren't valid for python
        identifiers so you can't access it with ``models.<name>``.

        Args:
            name (str): the name of the component as shown by :func:`Models.find()`.
        """
        comp = self.get(name) or dr.get_component(name)
        if not comp:
            return

        if not plugins.is_rule(comp):
            self._requested.add((name, comp))

        if comp in self._broker:
            return self._broker[comp]

        if comp in self._broker.exceptions or comp in self._broker.missing_requirements:
            self._dump_diagnostics(comp)
            return

        val = dr.run(comp, broker=self._broker).get(comp)

        if comp not in self._broker:
            if comp in self._broker.exceptions or comp in self._broker.missing_requirements:
                self._dump_diagnostics(comp)
            else:
                print("{} chose to skip.".format(dr.get_name(comp)))
        return val

    def __getattr__(self, name):
        return self.evaluate(name)

    # TODO: lot of room for improvement here...
    def make_rule(self, path=None, overwrite=False, pick=None):
        """
        Attempt to generate a rule based on models used so far.

        Args:
            path(str): path to store the rule.
            overwrite (bool): whether to overwrite an existing file.
            pick (str): Optionally specify which lines or line ranges
                to use for the rule body. "1 2 3" gets lines 1,2 and 3.
                "1 3-5 7" gets line 1, lines 3 through 5, and line 7.
        """
        import IPython

        ip = IPython.get_ipython()
        ignore = [
            r"=.*models\.",
            r"^(%|!|help)",
            r"make_rule",
            r"models\.(show|find).*",
            r".*\?$",
            r"^(clear|pwd|cd *.*|ll|ls)$",
        ]

        if pick:
            lines = [r[2] for r in ip.history_manager.get_range_by_str(pick)]
        else:
            lines = []
            for r in ip.history_manager.get_range():
                l = r[2]
                if any(re.search(i, l) for i in ignore):
                    continue
                elif l.startswith("models."):
                    l = l[7:]
                lines.append(l)

        # the user asked for these models during the session.
        requested = sorted(self._requested, key=lambda i: i[0])

        # figure out what we need to import for filtering.
        filterable = defaultdict(list)
        for _, c in requested:
            for d in dr.get_dependency_graph(c):
                try:
                    if isinstance(d, RegistryPoint) and d.filterable:
                        n = d.__qualname__
                        cls = n.split(".")[0]
                        filterable[dr.get_module_name(d)].append((cls, n))
                except:
                    pass

        model_names = [dr.get_simple_name(i[1]) for i in requested]
        var_names = [i[0].lower() for i in requested]

        imports = [
            "from insights import rule, make_fail, make_info, make_pass  # noqa",
            "from insights.parsr.query import *  # noqa",
            "from insights.parsr.query import make_child_query as q  # noqa",
            "",
        ]

        for _, c in requested:
            mod = dr.get_module_name(c)
            name = dr.get_simple_name(c)
            imports.append("from {} import {}".format(mod, name))

        seen = set()
        if filterable:
            imports.append("")

        for k in sorted(filterable):
            for (cls, n) in filterable[k]:
                if (k, cls) not in seen:
                    imports.append("from {} import {}".format(k, cls))
                    seen.add((k, cls))

        seen = set()
        filters = []
        for k in sorted(filterable):
            for i in filterable[k]:
                if i not in seen:
                    filters.append("add_filter({}, ...)".format(i[1]))
                    seen.add(i)

        if filters:
            imports.append("from insights.core.filters import add_filter")

        filter_stanza = os.linesep.join(filters)
        import_stanza = os.linesep.join(imports)
        decorator = "@rule({})".format(", ".join(model_names))
        func_decl = "def report({}):".format(", ".join(var_names))
        body = os.linesep.join(["    " + x for x in lines]) if lines else "    pass"

        res = import_stanza
        if filter_stanza:
            res += (os.linesep * 2) + filter_stanza

        res += (os.linesep * 3) + decorator + os.linesep + func_decl + os.linesep + body

        if path:
            if not path.startswith("/"):
                realpath = os.path.realpath(path)
                if not realpath.startswith(self._cwd):
                    path = os.path.join(self._cwd, path)

            if os.path.exists(path) and not overwrite:
                print(
                    "{} already exists. Use overwrite=True to overwrite.".format(path)
                )
                return

            if not os.path.exists(path) or overwrite:
                with open(path, "w") as f:
                    f.write(res)
                ip.magic("edit -x {}".format(path))
                print("Saved to {}".format(path))
        else:
            IPython.core.page.page(ip.pycolorize(res))

    def _desugar_match_ignore(self, match, ignore):
        if match is None:
            match = TRUE
        elif isinstance(match, str):
            if match in self:
                match = eq(dr.get_name(self[match]))
            else:
                match = matches(match)

        if ignore is None:
            ignore = FALSE
        elif isinstance(ignore, str):
            ignore = matches(ignore)

        return (match, ignore)

    def _show_missing(self, comp):
        results = []
        try:
            req, alo = self._broker.missing_requirements[comp]
            name = dr.get_name(comp)
            results.append(name)
            results.append("-" * len(name))
            if req:
                results.append("Requires:")
                for r in req:
                    results.append("    {}".format(dr.get_name(r)))
            if alo:
                if req:
                    results.append("")
                results.append("Requires At Least One From Each List:")
                for r in alo:
                    results.append("[")
                    for i in r:
                        results.append("    {}".format(dr.get_name(i)))
                    results.append("]")
        except:
            pass
        return results

    def show_requested(self):
        """ Show the components you've worked with so far. """
        results = []
        for name, comp in sorted(self._requested):
            results.append(
                ansiformat(
                    self._get_color(comp), "{} {}".format(name, dr.get_name(comp))
                )
            )
        IPython.core.page.page(six.u(os.linesep.join(results)))

    def reset_requested(self):
        """ Reset requested state so you can work on a new rule. """
        IPython.get_ipython().history_manager.reset()
        self._requested.clear()

    def show_source(self, comp):
        """
        Show source for the given module, class, or function. Also accepts
        the string names, with the side effect that the component will be
        imported.
        """
        try:
            if isinstance(comp, six.string_types):
                comp = self.get(comp) or dr.get_component(comp) or importlib.import_module(comp)
            comp = inspect.getmodule(comp)
            ip = IPython.get_ipython()
            if self._cov:
                path, runnable, excluded, not_run, _ = self._cov.analysis2(comp)
                runnable, not_run = set(runnable), set(not_run)
                src = ip.pycolorize(inspect.getsource(comp)).splitlines()
                width = len(str(len(src)))
                template = "{0:>%s}" % width
                results = []
                file_line = "{} {}".format(
                    ansiformat("red", "File:"), os.path.realpath(path)
                )
                explain_line = "{} numbered lines have executed. python standard libs are excluded.".format(
                    ansiformat("*brightgreen*", "Green")
                )
                results.append(file_line)
                results.append(explain_line)
                results.append("")
                for i, line in enumerate(src, start=1):
                    prefix = template.format(i)
                    if i in runnable and i not in not_run:
                        color = "*brightgreen*"
                    else:
                        color = "gray"
                    results.append("{} {}".format(ansiformat(color, prefix), line))
                IPython.core.page.page(six.u(os.linesep.join(results)))
            else:
                ip.inspector.pinfo(comp, detail_level=1)
        except:
            traceback.print_exc()

    def _get_type_name(self, comp):
        try:
            return dr.get_component_type(comp).__name__
        except:
            return ""

    def _get_rule_value_kind(self, val):
        if val is None:
            kind = None
        elif isinstance(val, plugins.make_response):
            kind = "fail"
        elif isinstance(val, plugins.make_pass):
            kind = "pass"
        elif isinstance(val, plugins.make_info):
            kind = "info"
        elif isinstance(val, plugins._make_skip):
            kind = "skip"
        elif isinstance(val, plugins.Response):
            kind = val.response_type or ""
        else:
            kind = ""
        return kind

    def _get_rule_value(self, comp):
        try:
            val = self._broker[comp]
            if plugins.is_rule(comp):
                _type = val.__class__.__name__
                kind = self._get_rule_value_kind(val)
                color = RULE_COLORS.get(kind, "")
                return ansiformat(color, " [{}]".format(_type))
        except:
            pass
        return ""

    def _show_datasource(self, d, v, indent=""):
        try:
            filtered = "filtered" if dr.DELEGATES[d].filterable else "unfiltered"
            mode = "bytes" if dr.DELEGATES[d].raw else "lines"
        except:
            filtered = "unknown"
            mode = "unknown"

        desc = "{n} ({f} / {m})".format(n=dr.get_name(d), f=filtered, m=mode)
        color = self._get_color(d)

        results = []
        results.append(indent + ansiformat(color, desc))

        if not v:
            return results
        if not isinstance(v, list):
            v = [v]

        for i in v:
            if isinstance(i, ContentProvider):
                s = ansiformat(color, str(i))
            else:
                s = ansiformat(color, "<intermediate value>")
            results.append("{}\u250A\u254C\u254C\u254C\u254C\u254C{}".format(indent, s))
        return results

    def _show_tree(self, node, indent="", depth=None, dep_getter=dr.get_dependencies):
        if depth is not None and depth == 0:
            return []

        results = []
        color = self._get_color(node)
        if plugins.is_datasource(node):
            results.extend(
                self._show_datasource(node, self._broker.get(node), indent=indent)
            )
        else:
            _type = self._get_type_name(node)
            name = dr.get_name(node)
            suffix = self._get_rule_value(node)
            desc = ansiformat(color, "{n} ({t}".format(n=name, t=_type))
            results.append(indent + desc + suffix + ansiformat(color, ")"))

        dashes = "\u250A\u254C\u254C\u254C\u254C\u254C"
        if node in self._broker.exceptions:
            for ex in self._broker.exceptions[node]:
                results.append(indent + dashes + ansiformat(color, str(ex)))

        deps = dep_getter(node)
        next_indent = indent + "\u250A   "
        for d in deps:
            results.extend(
                self._show_tree(
                    d, next_indent, depth=depth if depth is None else depth - 1, dep_getter=dep_getter
                )
            )
        return results

    def show_trees(self, match=None, ignore="spec", depth=None, toward_dependents=False):
        """
        Show dependency trees of any components whether they're available or not.

        Args:
            match (str, optional): regular expression for matching against
                the fully qualified name of components to keep.
            ignore (str, optional): regular expression for searching against
                the fully qualified name of components to ignore.
            depth (int, optional): how deep into the tree to explore.
            toward_dependents (bool, optional): whether to walk the tree toward dependents.
                Default is to walk toward dependencies.
        """
        match, ignore = self._desugar_match_ignore(match, ignore)
        dep_getter = dr.get_dependents if toward_dependents else dr.get_dependencies

        graph = defaultdict(list)
        for c in dr.DELEGATES:
            name = dr.get_name(c)
            if match.test(name) and not ignore.test(name):
                graph[name].append(c)

        results = []
        for name in sorted(graph):
            for c in graph[name]:
                results.extend(self._show_tree(c, depth=depth, dep_getter=dep_getter))
                results.append("")
        IPython.core.page.page(six.u(os.linesep.join(results)))

    def show_failed(self, match=None, ignore="spec"):
        """
        Show names of any components that failed during evaluation. Ignores
        "spec" by default.

        Args:
            match (str, optional): regular expression for matching against
                the fully qualified name of components to keep.
            ignore (str, optional): regular expression for searching against
                the fully qualified name of components to ignore.
        """
        match, ignore = self._desugar_match_ignore(match, ignore)

        mid_dashes = "\u250A\u254C\u254C"
        bottom_dashes = "\u2514\u254C\u254C"
        results = []
        for comp in sorted(self._broker.exceptions, key=dr.get_name):
            name = dr.get_name(comp)
            if match.test(name) and not ignore.test(name):
                color = self._get_color(comp)
                results.append(ansiformat(color, name))
                exes = self._broker.exceptions[comp]
                last = len(exes) - 1
                for i, ex in enumerate(exes):
                    dashes = bottom_dashes if i == last else mid_dashes
                    results.append(ansiformat(color, dashes + str(ex)))
                results.append("")
        IPython.core.page.page(six.u(os.linesep.join(results)))

    def _show_exceptions(self, comp):
        name = dr.get_name(comp)
        results = [ansiformat("*brightred*", name)]
        results.append(ansiformat("*brightred*", "-" * len(name)))
        for e in self._broker.exceptions.get(comp, []):
            t = self._broker.tracebacks.get(e)
            if t:
                results.append(t)
        return results

    def show_exceptions(self, match=None, ignore="spec"):
        """
        Show exceptions that occurred during evaluation. Ignores "spec" by
        default.

        Args:
            match (str, optional): regular expression for matching against
                the fully qualified name of components to keep.
            ignore (str, optional): regular expression for searching against
                the fully qualified name of components to ignore.
        """
        match, ignore = self._desugar_match_ignore(match, ignore)

        results = []
        for comp in sorted(self._broker.exceptions, key=dr.get_name):
            name = dr.get_name(comp)
            if match.test(name) and not ignore.test(name):
                results.extend(self._show_exceptions(comp))
        IPython.core.page.page(six.u(os.linesep.join(results)))

    def show_rule_report(self, match=None, ignore=None):
        """
        Print a rule report for the matching rules.
        """
        match, ignore = self._desugar_match_ignore(match, ignore)
        results = defaultdict(dict)

        for comp, val in self._broker.items():
            name = dr.get_name(comp)
            if plugins.is_rule(comp) and match.test(name) and not ignore.test(name):
                kind = self._get_rule_value_kind(val)

                if kind:
                    body = render(comp, val)
                    links = render_links(comp)
                    results[kind][name] = os.linesep.join([body, "", links])

        report = []
        for kind in ["info", "pass", "fail"]:
            color = RULE_COLORS.get(kind, "")
            hits = results.get(kind, {})
            for name in sorted(hits):
                report.append(ansiformat(color, name))
                report.append(ansiformat(color, "-" * len(name)))
                report.append(hits[name])
                report.append("")
        IPython.core.page.page(six.u(os.linesep.join(report)))

    def show_timings(self, match=None, ignore="spec", group=dr.GROUPS.single):
        """
        Show timings for components that have successfully evaluated.

        Args:
            match (str, optional): regular expression for matching against
                the fully qualified name of components to keep.
            ignore (str, optional): regular expression for searching against
                the fully qualified name of components to ignore.
        """
        match, ignore = self._desugar_match_ignore(match, ignore)

        results = []
        total = 0.0
        for comp in dr.COMPONENTS[group]:
            name = dr.get_name(comp)
            if comp in self._broker.exec_times and match.test(name) and not ignore.test(name):
                color = self._get_color(comp)
                t = self._broker.exec_times[comp]
                total += t
                results.append((t, name, color))

        report = [ansiformat("brightmagenta", "Total: {:.10f} seconds".format(total)), ""]
        for timing, name, color in sorted(results, reverse=True):
            report.append(ansiformat(color, "{:.10f}: {}".format(timing, name)))

        IPython.core.page.page(six.u(os.linesep.join(report)))

    def find(self, match=None, ignore=None):
        """
        Find components that might be available based on the data being
        analyzed.

        Args:
            match (str, optional): regular expression for matching against
                the fully qualified name of components to keep.
            ignore (str, optional): regular expression for searching against
                the fully qualified name of components to ignore.
        """
        match, ignore = self._desugar_match_ignore(match, ignore)
        mid_dashes = "\u250A\u254C\u254C"
        bottom_dashes = "\u2514\u254C\u254C"
        results = []
        for p in sorted(self, key=str.lower):
            comp = self[p]
            name = dr.get_name(comp)
            if match.test(name) and not ignore.test(name):
                color = self._get_color(comp)
                _type = self._get_type_name(comp)
                suffix = self._get_rule_value(comp)
                desc = ansiformat(color, "{p} ({n}, {t}".format(p=p, n=name, t=_type))
                results.append(desc + suffix + ansiformat(color, ")"))
                if comp in self._broker.exceptions:
                    exes = self._broker.exceptions[comp]
                    last = len(exes) - 1
                    for i, ex in enumerate(exes):
                        dashes = bottom_dashes if i == last else mid_dashes
                        results.append(ansiformat(color, dashes + str(ex)))
        IPython.core.page.page(six.u(os.linesep.join(results)))


class Holder(dict):
    """
    This is a dictionary that holds models for multiple archives. Access each model
    set using the path to the archive as the key. See models.keys().
    """
    def _ipython_key_completions_(self):
        return self.keys()


def start_session(paths, change_directory=False, __coverage=None, kernel=False):
    __cwd = os.path.abspath(os.curdir)

    def callback(brokers):
        models = Holder()
        for i, (path, broker) in enumerate(brokers):
            avail = _get_available_models(broker)
            if paths:
                if len(paths) > 1:
                    models[paths[i]] = Models(broker, avail, __cwd, path, __coverage)
                else:
                    models = Models(broker, avail, __cwd, path, __coverage)
            else:
                models = Models(broker, avail, __cwd, path, __coverage)

        if change_directory and len(brokers) == 1:
            __working_path, _ = brokers[0]
            os.chdir(__working_path)
        # disable jedi since it won't autocomplete for objects with__getattr__
        # defined.
        IPython.core.completer.Completer.use_jedi = False
        __cfg = Config()
        __cfg.TerminalInteractiveShell.banner1 = Models.__doc__
        __ns = {}
        __ns.update(globals())
        __ns.update({"models": models})

        if kernel:
            from ipykernel import kernelapp
            kernelapp.launch_new_instance([], user_ns=__ns, config=__cfg)
        else:
            IPython.start_ipython([], user_ns=__ns, config=__cfg)

    with_brokers(paths, callback)
    if change_directory:
        os.chdir(__cwd)


def _handle_config(config):
    if config:
        with open(config) as f:
            cfg = yaml.load(f, Loader=Loader)
            load_packages(cfg.get("packages", []))
            apply_default_enabled(cfg)
            apply_configs(cfg)


def _parse_args():
    desc = "Perform interactive system analysis with insights components."
    epilog = """
        Set env INSIGHTS_FILTERS_ENABLED=False to disable filtering that may
        cause unexpected missing data.
    """.strip()
    p = argparse.ArgumentParser(description=desc, epilog=epilog)

    p.add_argument(
        "-p", "--plugins", default="", help="Comma separated list of packages to load."
    )
    p.add_argument("-c", "--config", help="The insights configuration to apply.")
    p.add_argument(
        "--no-coverage",
        action="store_true",
        help="Don't show code coverage when viewing source.",
    )
    p.add_argument(
        "--cd",
        action="store_true",
        help="Change into the expanded directory for analysis.",
    )
    p.add_argument(
        "--no-defaults", action="store_true", help="Don't load default components."
    )
    p.add_argument(
        "-v", "--verbose", action="store_true", help="Global debug level logging."
    )
    p.add_argument(
        "-k", "--kernel", action="store_true", default=False,
        help="Start an IPython kernel instead of an interactive session."
        " Requires ipykernel module"
    )

    path_desc = "Archives or paths to analyze. Leave off to target the current system."
    p.add_argument("paths", nargs="*", help=path_desc)

    return p.parse_args()


def main():
    args = _parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.ERROR)

    cov = None
    if not args.no_coverage:
        from coverage import Coverage

        cov = Coverage(cover_pylib=False)
        cov.start()

    if not args.no_defaults:
        load_default_plugins()
        dr.load_components("insights.parsers", "insights.combiners")

    load_packages(parse_plugins(args.plugins))
    _handle_config(args.config)

    start_session(args.paths, args.cd, __coverage=cov, kernel=args.kernel)
    if cov:
        cov.stop()
        cov.erase()


if __name__ == "__main__":
    main()
