#!/usr/bin/env python
"""
Creates the content used to describe files and command output to be
collected by the client-side Red Hat Insights uploder.  That is,
it creates the ``uploader.json`` file.

In addition, it creates a mapping of files to plugins,
``file_plugin_mapping.json``, to be used to identify what plugins would
be effectively turned off by blacklisting a specific file.
"""

from collections import defaultdict
from datetime import datetime
import json
import logging
import os
import sys
from optparse import OptionParser

# This is pretty hacky, but lets us run this w/o a virtualenv
try:
    import insights
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    import insights

from insights.config import CommandSpec, SimpleFileSpec
from insights.config import get_meta_specs
from insights.core import plugins, DEFAULT_PLUGIN_MODULE
from insights.config import InsightsDataSpecConfig, specs as config_specs, group_wrap

log = logging.getLogger()


class APIConfigGenerator(object):

    def __init__(self,
                 data_spec_config=None,
                 uploader_config_filename="uploader.json",
                 file_plugin_map_filename="file_plugin_mapping.json",
                 rule_spec_mapping_filename="rule_spec_mapping.json",
                 plugin_package=None,
                 version_number=None):

        if data_spec_config is None:
            self.data_spec_config = InsightsDataSpecConfig(
                config_specs.static_specs,
                config_specs.meta_files, pre_commands=config_specs.pre_commands)
        else:
            self.data_spec_config = data_spec_config
        self.openshift_config = InsightsDataSpecConfig(config_specs.openshift,
                                                       {}, prefix="openshift")
        self.uploader_config_filename = uploader_config_filename
        self.file_plugin_map_filename = file_plugin_map_filename
        self.rule_spec_mapping_filename = rule_spec_mapping_filename
        self.rule_spec_mapping = defaultdict(lambda: defaultdict(list))

        if version_number:
            self.version_number = version_number
        else:
            self.version_number = os.environ.get("BUILD_NUMBER",
                                                 datetime.now().isoformat())

        plugins.load(plugin_package if plugin_package else DEFAULT_PLUGIN_MODULE)

    @staticmethod
    def writefile(filename, o):
        with open(filename, "wb") as fp:
            fp.write(json.dumps(o, indent=4, separators=(',', ': '), sort_keys=True))

    @staticmethod
    def get_filters_for(name):
        return list(plugins.NAME_TO_FILTER_MAP.get(name, ()))

    @staticmethod
    def get_rule_ids_for(plugin):
        mod = sys.modules[plugin.__module__]
        for mem, val in vars(mod).items():
            if mem.startswith("ERROR_KEY"):
                yield "{0}|{1}".format(
                    plugin.__module__.split(".")[-1],
                    val)

    class UploaderSpecs:

        def __init__(self):
            self._LIST = {}

        def add(self, name, spec, output_filters):
            self._LIST[name] = spec.add_uploader_spec(self.get_one(name), output_filters)

        def get_one(self, name):
            if name in self._LIST:
                return self._LIST[name]
            else:
                return None

        def get_all(self):
            return self._LIST

    def serialize_data_spec(self):
        # really don't like the instanceof checking..
        upload_conf = {
            "version": self.version_number,
            "commands": [],
            "files": [
                {"file": "/etc/redhat-access-insights/machine-id", "pattern": []},
                {"file": "/etc/redhat_access_proactive/machine-id", "pattern": []}
            ],
            "openshift": [],
        }

        # these lists are used to allow for sorting of the output mapping
        # I'm assuming that the iteration order of dict items is equal
        # to the insertion order
        specs_list = self.UploaderSpecs()

        specs_list.add("machine-id1", SimpleFileSpec("etc/redhat-access-insights/machine-id"), [])
        specs_list.add("machine-id2", SimpleFileSpec("etc/redhat_access_proactive/machine-id"), [])
        added_paths = defaultdict(set)
        utilized_specs = set()

        def add_name(name, plugins, sc):
            specs = sc.get_specs(name)
            for s in specs:
                utilized_specs.add(s)
            conf = upload_conf[sc.prefix] if sc.prefix else upload_conf
            for spec in specs:
                output_filter = sorted(self.get_filters_for(name))
                specs_list.add(name, spec, output_filter)
                path = spec.get_for_uploader()
                if isinstance(spec, CommandSpec):
                    pk_key = spec.get_pre_command_key()
                    cmd = {"command": path, "pattern": output_filter}
                    if pk_key:
                        cmd["pre_command"] = pk_key

                    lst = conf if sc.prefix else conf["commands"]
                    lst.append(cmd)
                    spec_key = "commands"

                else:
                    if path not in added_paths[sc]:
                        lst = conf if sc.prefix else conf["files"]
                        lst.append({
                            "file": path,
                            "pattern": output_filter
                        })
                        spec_key = "files"
                        added_paths[sc].add(path)
                    else:
                        continue

                for plugin in plugins_:
                    for rule_id in self.get_rule_ids_for(plugin):
                        self.rule_spec_mapping[rule_id][spec_key].append(path)

        for name in sorted(plugins.PARSERS):
            plugins_ = plugins.PARSERS[name]
            if not any(m for m in plugins_ if m.consumers):
                continue
            spec_configs = (self.data_spec_config, self.openshift_config)
            if all(map(lambda sc: sc.get_specs(name) == [], spec_configs)):
                error_msg = ("Symbolic name '{0}' is referenced by '{1}', "
                             "but is not available via configuration.")
                dependent_plugins = ", ".join([p.__module__ for p in plugins_])
                print error_msg.format(name, dependent_plugins)
                continue
            for sc in spec_configs:
                add_name(name, plugins_, sc)

        print "*" * 80
        all_specs = set()
        reverse_map = {}
        for symbolic_name, sc in group_wrap(config_specs.static_specs).iteritems():
            for s in sc.get_specs():
                reverse_map[s] = symbolic_name
                all_specs.add(s)
        missing_specs = " ".join(sorted(set(reverse_map[i] for i in (all_specs - utilized_specs))))
        print "%d specs not included in uploader.json: %s" % (
            len(all_specs - utilized_specs),
            missing_specs)
        # placing the log at the end of the list ensures that we log as much
        # as possible before copying the logfile
        upload_conf["files"].append({
            "file": "/var/log/redhat-access-insights/redhat-access-insights.log",
            "pattern": []
        })
        upload_conf["files"].append({
            "file": "/var/log/redhat_access_proactive/redhat_access_proactive.log",
            "pattern": []
        })

        upload_conf["specs"] = specs_list.get_all()
        upload_conf["meta_specs"] = get_meta_specs()
        upload_conf["pre_commands"] = self.data_spec_config.pre_commands

        return upload_conf

    def create_file_content(self):

        upload_conf = self.serialize_data_spec()

        # Holds the data that becomes file_plugin_mapping.json
        file_plugins_map = defaultdict(list)

        for filename, plugin_classes in plugins.PARSERS.iteritems():
            for plugin_class in plugin_classes:
                file_plugins_map[filename].append(plugin_class.__module__)

        self.writefile(self.uploader_config_filename, upload_conf)
        self.writefile(self.file_plugin_map_filename, file_plugins_map)
        self.writefile(self.rule_spec_mapping_filename, self.rule_spec_mapping)


def main():
    p = OptionParser()
    p.add_option("-v", "--verbose", dest="verbose",
                 help="log more things",
                 action="store_true", default=False)
    opts, args = p.parse_args()

    if len(args) == 0:
        print "Plugin package name required"
        sys.exit(1)

    level = logging.DEBUG if opts.verbose else logging.INFO
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                        level=level)
    log.info("Generating config files from %s.", insights.get_nvr())
    config_generator = APIConfigGenerator(plugin_package=args[0])
    config_generator.create_file_content()


if __name__ == "__main__":
    main()
