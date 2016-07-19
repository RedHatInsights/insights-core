import argparse
import glob
import imp
import logging
import os
import sys
import json
from collections import defaultdict
from falafel.console.format import Formatter
from falafel.core import plugins


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

    def handle_sosreport(self, path):
        from falafel.core import archives, specs, evaluators
        from falafel.config.static import get_config
        from falafel.config import group_wrap
        config = get_config()

        if self.args.specs:
            try:
                my_specs = imp.load_source("specs", self.args.specs)
                config.merge(group_wrap(my_specs.specs))
            except ImportError:
                logging.error("Failed to load specs module.", exc_info=True)

        reports = []
        with archives.OnDiskExtractor() as ex:
            tf = ex.from_path(path)
            sm = specs.SpecMapper(tf, data_spec_config=config)
            for name, paths in self.external_files.iteritems():
                for path in paths:
                    ext_path = os.path.join("external", path)
                    sm.symbolic_files[name].append(ext_path)

            md_str = sm.get_content("metadata.json", split=False, default="{}")
            md = json.loads(md_str)
            if md and 'systems' in md:
                runner = evaluators.MultiEvaluator(sm, metadata=md)
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
    parser = argparse.ArgumentParser(description="Evaluate a sosreport for some rules.")
    parser.add_argument("--sosreport", help="path to a sosreport to analyze (the path can be to a tar file, or to an expanded directory tree)")
    parser.add_argument("--ext-file", dest="external_files", nargs="*", help="key=value set of a file to include for analysis")
    parser.add_argument("--specs", dest="specs", help="module path to user-defined specs")
    parser.add_argument("--plugin-modules", dest="plugin_modules", nargs="*", help="path to extra plugins")
    parser.add_argument("--hide-plugin-list", dest="list_plugins", action="store_false", default=True, help="Hide full plugin listing")
    parser.add_argument("--hide-missing", dest="list_missing", action="store_false", default=True, help="Hide missing file listing")
    parser.add_argument("--max-width", dest="max_width", action="store", type=int, default=0, help="Max output width.  Defaults to width of console")
    parser.add_argument("--verbose", "-v", dest="verbose", action="count", default=0)

    args = parser.parse_args()
    args.list_missing = False  # Force suppression until we make it work again

    log_level = {0: logging.ERROR, 1: logging.INFO}.get(args.verbose, logging.DEBUG)
    logging.basicConfig(level=log_level)

    runner = Runner(args)

    if not args.plugin_modules:
        logging.error("At least one plugin module must be specified.")
        sys.exit(1)

    for module in args.plugin_modules:
        logging.info("Loading %s", module)
        plugins.load(module)

    if args.sosreport:
        Formatter(args).format_results(*runner.handle_sosreport(args.sosreport))

if __name__ == "__main__":
    main()
