import argparse
import logging
import os
import re
import yaml

from collections import defaultdict
from contextlib import contextmanager

from insights.parsr.query import *  # noqa
from insights.parsr.query import matches, make_child_query as q  # noqa
from insights.parsr.query.boolean import FALSE, TRUE

from insights import apply_configs, create_context, datasource, dr, extract, load_default_plugins, load_packages, parse_plugins
from insights.core import plugins
from insights.core.context import HostContext
from insights.core.spec_factory import ContentProvider, RegistryPoint


Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--plugins", default="")
    p.add_argument("-c", "--config")
    p.add_argument("--cd", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("path", nargs="?")
    return p.parse_args()


@contextmanager
def create_new_broker(path):
    datasources = dr.get_components_of_type(datasource)

    def make_broker(ctx):
        broker = dr.Broker()
        broker[ctx.__class__] = ctx

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


def __get_available_models(broker):
    state = set(broker.instances.keys())
    models = {}

    for comp in dr.run_order(dr.COMPONENTS[dr.GROUPS.single]):
        if comp in dr.DELEGATES and not plugins.is_datasource(comp):
            if dr.DELEGATES[comp].get_missing_dependencies(state):
                continue

            if plugins.is_type(comp, (plugins.rule, plugins.condition, plugins.incident)):
                name = "_".join([dr.get_base_module_name(comp), dr.get_simple_name(comp)])
            else:
                name = dr.get_simple_name(comp)

            name = name
            if name in models:
                prev = models[name]
                models[dr.get_name(prev).replace(".", "_")] = prev

                del models[name]
                name = dr.get_name(comp).replace(".", "_")

            models[name] = comp
            state.add(comp)

    return models


class __Models(dict):
    def __init__(self, broker, models, cwd):
        self._requested = set()
        self._broker = broker
        self._cwd = cwd
        super().__init__(models)

    def __dir__(self):
        return sorted(self.keys())

    def _dump_diagnostics(self, comp):
        print("Missing Dependencies")
        print("====================")
        self._show_missing(comp)
        print()
        print("Exceptions")
        print("==========")
        self._show_exceptions(comp)
        print()
        print("Dependency Tree")
        print("===============")
        self._show_tree(comp)

    def evaluate(self, name):
        comp = self.get(name)
        if not comp:
            return

        self._requested.add((name, comp))

        if comp in self._broker:
            return self._broker[comp]

        if comp in self._broker.exceptions or comp in self._broker.missing_requirements:
            self._dump_diagnostics(comp)
            return None

        val = dr.run(comp, broker=self._broker).get(comp)
        if comp not in self._broker:
            if comp in self._broker.exceptions or comp in self._broker.missing_requirements:
                self._dump_diagnostics(comp)
            else:
                print("{} chose to skip.".format(dr.get_name(comp)))
        return val

    def __getattr__(self, name):
        return self.evaluate(name)

    # TODO: oh man this function is gross...
    def make_rule(self, path=None, overwrite=False, pick=None):
        import IPython
        ip = IPython.get_ipython()
        ignore = [
            r"=.*models\.",
            r"^(%|!|help)",
            r"make_rule",
            r"models\.show.*",
            r".*\?$",
            r"^(clear|pwd|cd *.*|ll|ls)$"
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

        requested = sorted(self._requested, key=lambda i: i[0])
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
            ""
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

        filter_stanza = "\n".join(filters)
        import_stanza = "\n".join(imports)
        decorator = "@rule({})".format(", ".join(model_names))
        func_decl = "def report({}):".format(", ".join(var_names))
        body = "\n".join(["    " + l for l in lines]) if lines else "    pass"

        res = import_stanza
        if filter_stanza:
            res += "\n\n" + filter_stanza

        res += "\n\n\n" + decorator + "\n" + func_decl + "\n" + body

        if path:
            if not path.startswith("/"):
                realpath = os.path.realpath(path)
                if not realpath.startswith(self._cwd):
                    path = os.path.join(self._cwd, path)

            if os.path.exists(path) and not overwrite:
                print("{} already exists. Use overwrite=True to overwrite.".format(path))
                return

            if not os.path.exists(path) or overwrite:
                with open(path, "w") as f:
                    f.write(res)
        else:
            print(res)

    def _desugar_match_ignore(self, match, ignore):
        if match is None:
            match = TRUE
        elif isinstance(match, str):
            match = matches(match)

        if ignore is None:
            ignore = FALSE
        elif isinstance(ignore, str):
            ignore = matches(ignore)

        return (match, ignore)

    def _show_missing(self, comp):
        try:
            req, alo = self._broker.missing_requirements[comp]
            name = dr.get_name(comp)
            print(name)
            print("-" * len(name))
            if req:
                print("Requires:")
                for r in req:
                    print("    {}".format(dr.get_name(r)))
            if alo:
                if req:
                    print()
                print("Requires At Least One From Each List:")
                for r in alo:
                    print("[")
                    for i in r:
                        print("    {}".format(dr.get_name(i)))
                    print("]")
        except:
            pass

    def _show_datasource(self, d, v, indent=""):
        try:
            filtered = "filtered" if dr.DELEGATES[d].filterable else "unfiltered"
            mode = "bytes" if dr.DELEGATES[d].raw else "lines"
        except:
            filtered = "unknown"
            mode = "unknown"

        desc = "{n} ({f} / {m})".format(n=dr.get_name(d), f=filtered, m=mode)
        print(indent + desc)

        if not v:
            return
        if not isinstance(v, list):
            v = [v]

        if not v:
            return

        for i in v:
            if isinstance(i, ContentProvider):
                print("{}\u250A\u254C\u254C\u254C\u254C{}".format(indent, i))
            else:
                print("{}\u250A\u254C\u254C\u254C\u254C<intermediate value>".format(indent))

    def _show_tree(self, node, indent=""):
        if plugins.is_datasource(node) and node in self._broker:
            self._show_datasource(node, self._broker[node], indent=indent)
        else:
            print(indent + dr.get_name(node))

        deps = dr.get_dependencies(node)
        next_indent = indent + "\u250A   "
        if deps:
            for d in deps:
                self._show_tree(d, next_indent)

    def show_trees(self, match=None, ignore=None):
        match, ignore = self._desugar_match_ignore(match, ignore)

        graph = defaultdict(list)
        for c in set(self.values()) | set(self._broker.instances):
            name = dr.get_name(c)
            if match.test(name) and not ignore.test(name):
                graph[name].append(c)

        for name in sorted(graph):
            for c in graph[name]:
                self._show_tree(c)
                print()

    def show_failed(self, match=None, ignore=None):
        match, ignore = self._desugar_match_ignore(match, ignore)

        for c in sorted(set(dr.get_name(comp) for comp in self._broker.exceptions)):
            if match.test(c) and not ignore.test(c):
                print(c)

    def _show_exceptions(self, comp):
        name = dr.get_name(comp)
        print(name)
        print("-" * len(name))
        for e in self._broker.exceptions.get(comp, []):
            t = self._broker.tracebacks.get(e)
            if t:
                print(t)

    def show_exceptions(self, match=None, ignore=None):
        match, ignore = self._desugar_match_ignore(match, ignore)

        for comp in sorted(self._broker.exceptions, key=dr.get_name):
            name = dr.get_name(comp)
            if match.test(name) and not ignore.test(name):
                self._show_exceptions(comp)

    def find(self, match=None, ignore=None):
        match, ignore = self._desugar_match_ignore(match, ignore)
        for p in sorted(self, key=str.lower):
            name = dr.get_name(self[p])
            if match.test(name) and not ignore.test(name):
                print("{p} ({name})".format(p=p, name=name))


def start_session(__path, change_directory=False):
    import IPython
    from traitlets.config.loader import Config

    with create_new_broker(__path) as (__working_path, __broker):
        __cwd = os.path.abspath(os.curdir)
        __models = __get_available_models(__broker)
        models = __Models(__broker, __models, __cwd)
        if change_directory:
            os.chdir(__working_path)

        IPython.core.completer.Completer.use_jedi = False
        __cfg = Config()
        __ns = {}
        __ns.update(globals())
        __ns.update(locals())
        IPython.start_ipython([], user_ns=__ns, config=__cfg)

        # TODO: we could automatically save the session here
        # see Models.make_rule
        if change_directory:
            os.chdir(__cwd)


def handle_config(config):
    if config:
        with open(config) as f:
            apply_configs(yaml.load(f, Loader=Loader))


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.ERROR)

    load_default_plugins()
    dr.load_components("insights.parsers", "insights.combiners")

    load_packages(parse_plugins(args.plugins))
    handle_config(args.config)

    start_session(args.path, args.cd)


if __name__ == "__main__":
    main()
