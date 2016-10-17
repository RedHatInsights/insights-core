import argparse
import glob
import imp
import logging
import os
import sys
import json
from collections import defaultdict
from falafel.console.custom_logging import setup_logger
from falafel.console.format import Formatter
from falafel.console.config import InsightsCliConfig
from falafel.console.package import get_plugin_modules
from falafel.core import plugins
from falafel.core import get_module_names
from falafel.console.custom_logging import print_console, ERROR_MSG

logger = logging.getLogger(__name__)


class Runner(object):

    def __init__(self, args):
        self.args = args
        self.external_files = defaultdict(list)

        if self.args.external_files:
            for pair in self.args.external_files:
                if "=" not in pair:
                    raise Exception("external files must be specified in name=path pairs")

                name, path = pair.split("=")
                for p in glob.glob(path):
                    logging.info("Adding '%s' as an external file for name '%s'", p, name)
                    self.external_files[name].append(p)

    def handle_sosreport(self, path, spec_map=None):
        from falafel.core import archives, specs, evaluators
        from falafel.config.static import get_config
        from falafel.config import group_wrap
        config = get_config()
        logging.info("Analyzing report '%s'", path)

        if self.args.specs:
            try:
                my_specs = imp.load_source("specs", self.args.specs)
                config.merge(group_wrap(my_specs.specs))
            except ImportError:
                logging.exception("Failed to load specs module.")

        reports = []
        ex_class = archives.OnDiskExtractor if not self.args.mem_only else archives.InMemoryExtractor
        with ex_class() as ex:
            tf = ex.from_path(path, self.args.extract_dir)
            sm = specs.SpecMapper(tf, data_spec_config=config)
            for name, paths in self.external_files.iteritems():
                for path in paths:
                    ext_path = os.path.join("external", path)
                    sm.symbolic_files[name].append(ext_path)

            md_str = sm.get_content("metadata.json", split=False, default="{}")
            md = json.loads(md_str)
            if spec_map:
                print json.dumps(sm.symbolic_files, indent=4, sort_keys=True)
                sys.exit(0)
            if md and 'systems' in md:
                runner = evaluators.InsightsMultiEvaluator(sm, metadata=md)
            else:
                if sm.exists("etc/redhat_access_insights/machine-id", symbolic=False):
                    runner = evaluators.InsightsSingleEvaluator(sm)
                else:
                    runner = evaluators.SingleEvaluator(sm)

            results = runner.process()
            system = results.get("system", {})
            reports = self.reports_generator(results.get("reports", []))
            if sm.analysis_target:
                system["analysis_target"] = sm.analysis_target.section_name
            return system, reports, self.extract_archives(results, md)

    def reports_generator(self, reports):
        results = {}
        for result in reports:
            module = result["rule_id"].split("|")[0]
            results[module] = result["details"]

        for module, d in plugins.PLUGINS.iteritems():
            module = module.split(".")[-1]
            yield module, None, results.get(module)

    def extract_archives(self, results, md):
        results_archives = results.get("archives", None)
        if results_archives:
            archives = []
            for each in results_archives:
                archives.append({"system": each.get("system", {}),
                                 "reports": self.reports_generator(each.get("reports", []))})
            return archives
        else:
            return None


def main():
    cfg = InsightsCliConfig()

    parser = argparse.ArgumentParser(description="Evaluate a sosreport for some rules.")
    parser.add_argument("--extract-dir", dest="extract_dir", action="store", default=cfg.extract_dir, help="Root directory path in which files will be extracted.")
    parser.add_argument("--ext-file", dest="external_files", nargs="*", default=cfg.external_files, help="key=value set of a file to include for analysis")
    parser.add_argument("--specs", dest="specs", default=cfg.specs, help="module path to user-defined specs")
    parser.add_argument("--plugin-modules", dest="plugin_modules", nargs="*", default=cfg.plugin_modules, help="path to extra plugins")
    parser.add_argument("--show-plugin-list", dest="list_plugins", action="store_true", default=cfg.list_plugins, help="Show full plugin listing")
    parser.add_argument("--show-plugin-modules", dest="list_plugin_modules", action="store_true", help="Show full plugin modules listing")
    parser.add_argument("--hide-missing", dest="list_missing", action="store_false", default=cfg.list_missing, help="Hide missing file listing")
    parser.add_argument("--max-width", dest="max_width", action="store", type=int, default=cfg.max_width, help="Max output width.  Defaults to width of console")
    parser.add_argument("--verbose", "-v", dest="verbose", action="count", default=cfg.verbose)
    parser.add_argument("--spec-map", dest="spec_map", action="store_true", default=cfg.spec_map, help="Print the spec file mapping and exit")
    parser.add_argument("--mem-only", dest="mem_only", action="store_true", default=cfg.mem_only, help="Use in-memory extracter")
    parser.add_argument("reports", nargs="*", help="path to a report to analyze (the path can be to a tar file, or to an expanded directory tree)")

    args = parser.parse_args()
    args.list_missing = False  # Force suppression until we make it work again

    setup_logger(args.verbose)

    # log the command and arguments passed
    logging.info(" ".join(sys.argv))

    runner = Runner(args)
    frmt = Formatter(args)

    if args.list_plugin_modules:
        frmt.heading('Plugin Modules')
        plugin_modules = get_plugin_modules()
        frmt.display_list(plugin_modules)
        sys.exit(0)

    if not args.plugin_modules:
        logging.error("At least one plugin module must be specified.")
        print_console(ERROR_MSG, verbose=False)
        sys.exit(1)

    import_failures = []
    for module in args.plugin_modules:
        logging.info("Loading %s", module)
        try:
            plugins.load(module)
        except ImportError as e:
            import traceback
            import_failures.append(traceback.format_exc())
            logging.error("Error loading module: %s", module)
            if "Import by filename" in e.message:
                logging.error('Perhaps try adding "--" to the end of --plugin-modules arguments, e.g. "--plugin-modules my.plugins --"')

    # Wait to exit until all module imports have been attempted
    if import_failures:
        if args.verbose:
            for e in import_failures:
                logging.error(e.strip())
        else:
            print_console(ERROR_MSG, verbose=False)
        sys.exit(1)

    if not args.reports:
        if args.list_plugins:
            for plugin in args.plugin_modules:
                frmt.heading(plugin)
                module_list = [mod_name.split(".")[-1] for mod_name in get_module_names(sys.modules[plugin])]
                frmt.display_list(module_list)
            sys.exit(0)
        else:
            logging.error("Please specify at least one report to process")
            print_console(ERROR_MSG, verbose=False)
            sys.exit(1)

    for report in args.reports:
        frmt.format_results(*runner.handle_sosreport(report, args.spec_map))

if __name__ == "__main__":
    main()
