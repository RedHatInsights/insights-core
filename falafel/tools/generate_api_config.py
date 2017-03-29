#!/usr/bin/env python
"""
Creates the content used to describe files and command output to be
collected by the client-side Red Hat Insights uploder.  That is,
it creates the ``uploader.json`` file.

In addition, it creates a mapping of files to plugins,
``file_plugin_mapping.json``, to be used to identify what plugins would
be effectively turned off by blacklisting a specific file.
"""

from collections import defaultdict, OrderedDict
from datetime import datetime
import json
import logging
import os
import sys
from optparse import OptionParser

# This is pretty hacky, but lets us run this w/o a virtualenv
try:
    import falafel
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    import falafel

from falafel.config import CommandSpec, SimpleFileSpec
from falafel.config import DefaultAnalysisTargets
from falafel.config import get_meta_specs
from falafel.core import plugins, DEFAULT_PLUGIN_MODULE
from falafel.config.factory import get_config

log = logging.getLogger()


class APIConfigGenerator(object):

    def __init__(self,
                 data_spec_config=get_config(),
                 uploader_config_filename="uploader.json",
                 file_plugin_map_filename="file_plugin_mapping.json",
                 rule_spec_mapping_filename="rule_spec_mapping.json",
                 plugin_package=None,
                 version_number=None):

        self.data_spec_config = data_spec_config
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
            fp.write(json.dumps(o, indent=4, separators=(',', ': ')))

    @staticmethod
    def get_filters_for(name):
        return list(plugins.NAME_TO_FILTER_MAP.get(name, ()))

    @staticmethod
    def get_applies_to_for(mappers):
        # collect all the sets of kinds of reports that this list of mappers applies to

        # each plugin may apply to one, some, or all of the different kinds of reports
        #   plugins can indicate that they don't apply to all reports by setting a non-empty
        #   PLUGIN_APPLIES_TO to list of reports the plugin applies to.
        #   empty or non-existant PLUGIN_APPLIES_TO indicates that it applies to ALL kinds or reports
        #      (because this is the best default for now)
        # each plugin looks for one or more specs
        # each spec (file or command) may be used by one or more plugins
        #   if a spec is never needed for a particular report kind we want to indicate that
        #   in uploader.json

        # if a plugin doesn't restrict itself, then it appies to all report kinds
        # and all specs used by that plugin apply to all report kinds
        # and we can short circut this loop and return an empty set to indicate all kinds of reports

        retval = set()
        for mapper in mappers:
            dict = vars(sys.modules[mapper.__module__])
            if 'PLUGIN_APPLIES_TO' in dict:
                this_set = set(dict['PLUGIN_APPLIES_TO'])
                if this_set is None or this_set == set():
                    return None
                else:
                    retval |= this_set
            else:
                return None

        # if we get here then all mappers had some restriction
        # we now have the union of all the restrictions
        # but it is possible that the union of all the restrictions has resulted in all
        if retval == DefaultAnalysisTargets:
            return None
        else:
            return retval

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
            self._LIST = OrderedDict()

        def add(self, name, spec, output_filters):
            self._LIST[name] = spec.add_uploader_spec(self.get_one(name), output_filters)

        def get_one(self, name):
            if name in self._LIST:
                return self._LIST[name]
            else:
                return None

        def get_all(self):
            v = self._LIST
            self._LIST = OrderedDict()
            return v

    def serialize_data_spec(self):
        # really don't like the instanceof checking..
        upload_conf = {
            "version": self.version_number,
            "commands": [],
            "files": []
        }

        # these lists are used to allow for sorting of the output mapping
        # I'm assuming that the iteration order of dict items is equal
        # to the insertion order
        cmd_list = []
        specs_list = self.UploaderSpecs()
        whitelist = {
            "/etc/redhat-access-insights/machine-id": [],
            "/etc/redhat_access_proactive/machine-id": []
        }

        specs_list.add("machine-id1", SimpleFileSpec("etc/redhat-access-insights/machine-id"), [])
        specs_list.add("machine-id2", SimpleFileSpec("etc/redhat_access_proactive/machine-id"), [])

        for name in sorted(plugins.MAPPERS):
            plugins_ = plugins.MAPPERS[name]
            if not any(m for m in plugins_ if m.consumers):
                continue
            specs = self.data_spec_config.get_specs(name)
            if not specs:
                if name not in self.data_spec_config:
                    print "Symbolic name '{0}' is referenced by '{1}', but is not available via configuration.".format(
                        name, ", ".join([p.__module__ for p in plugins_]))
                continue

            for spec in specs:
                path = None
                spec_key = None

                output_filter = self.get_filters_for(name)

                specs_list.add(name, spec, output_filter)

                path = spec.get_for_uploader()
                if isinstance(spec, CommandSpec):
                    pk_key = spec.get_pre_command_key()
                    cmd_list.append((path, output_filter, pk_key))
                    spec_key = "commands"

                else:
                    if path not in whitelist:
                        whitelist[path] = output_filter
                        spec_key = "files"

                for plugin in plugins_:
                    for rule_id in self.get_rule_ids_for(plugin):
                        self.rule_spec_mapping[rule_id][spec_key].append(
                            path)

        for cmd, pattern, pre_command in sorted(cmd_list):
            r = {"command": cmd, "pattern": sorted(pattern)}
            if pre_command:
                r["pre_command"] = pre_command
            upload_conf["commands"].append(r)

        for path, pattern in sorted(whitelist.items()):
            upload_conf["files"].append(
                {"file": path, "pattern": sorted(pattern)})

        # placing the log at the end of the list ensures that we log as much
        # as possible before copying the logfile
        upload_conf["files"].append({
            "file": "/var/log/redhat-access-insights/redhat-access-insights.log",
            "pattern": []})
        upload_conf["files"].append({
            "file": "/var/log/redhat_access_proactive/redhat_access_proactive.log",
            "pattern": []})

        upload_conf["specs"] = specs_list.get_all()
        upload_conf["meta_specs"] = get_meta_specs()
        upload_conf["pre_commands"] = self.data_spec_config.pre_commands

        return upload_conf

    def create_file_content(self):

        upload_conf = self.serialize_data_spec()

        # Holds the data that becomes file_plugin_mapping.json
        file_plugins_map = defaultdict(list)

        for filename, plugin_classes in plugins.MAPPERS.iteritems():
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
    log.info("Generating config files from %s.", falafel.get_nvr())
    config_generator = APIConfigGenerator(get_config(), plugin_package=args[0])
    config_generator.create_file_content()


if __name__ == "__main__":
    main()
