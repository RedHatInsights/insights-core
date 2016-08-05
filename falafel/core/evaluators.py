import json
from collections import defaultdict

from falafel.core import archives, specs, marshalling, plugins
from falafel.core.marshalling import Marshaller
from falafel.core.plugins import validate_response
from falafel.core.context import Context
from falafel.core.archives import InvalidArchive
from falafel.util.uname import Uname
from falafel.core import reducer

import logging
log = logging.getLogger("eval")

marshaller = Marshaller()


def name_from_module(plugin):
    return plugin.__name__.rpartition(".")[-1]


class Evaluator(object):

    def is_pattern_file(self, symbolic_name):
        return self.spec_mapper.data_spec_config.is_multi_output(symbolic_name)

    def __init__(self, spec_mapper, metadata=None):
        self.spec_mapper = spec_mapper
        self.metadata = {}
        self.reducer_errors = []
        self.reducer_results = []
        self.archive_metadata = metadata

    def pre_mapping(self):
        pass

    def format_response(self, response):
        return response

    def format_result(self, result):
        return result

    def handle_reducer_error(self):
        def default_error_handler(func, e, local, shared):
            log.exception("Reducer [%s] failed", ".".join([func.__module__, func.__name__]))
        return default_error_handler

    def get_contextual_hostname(self, default=""):
        return self.hostname if hasattr(self, "hostname") and self.hostname else default

    def run_metadata_mappers(self, the_meta_data):
        MD_JSON = "metadata.json"
        result_map = {}
        for plugin in plugins.get_mappers(MD_JSON):
            context = self.build_context(content=marshalling.marshal(the_meta_data), path=MD_JSON)
            try:
                r = plugin(context)
                if r:
                    result_map[plugin] = [r]
            except Exception as e:
                self.handle_map_error(e, context)
        return result_map

    def build_context(self, content, path, **kwargs):
        kwargs.update({
            "content": content,
            "path": path,
            "hostname": self.get_contextual_hostname(),
            "release": self.release if hasattr(self, "release") else "",
            "version": self.uname.rhel_release if hasattr(self, "uname") and hasattr(self.uname, "rhel_release") else ['-1', '-1'],
        })
        if self.archive_metadata:
            kwargs["metadata"] = self.archive_metadata
        return Context(**kwargs)

    def process(self):
        self.pre_mapping()
        self.run_mappers()
        self.run_reducers()
        return self.get_response()

    def post_process(self):
        pass

    def handle_map_error(self, e, context):
        log.exception("Mapper failed")


class SingleEvaluator(Evaluator):

    def __init__(self, spec_mapper, metadata=None):
        super(SingleEvaluator, self).__init__(spec_mapper, metadata)
        self.mapper_results = defaultdict(list)

    def append_metadata(self, r):
        for k, v in r.iteritems():
            self.metadata[k] = v

    def pre_mapping(self):
        self.release = self._protected_parse("redhat-release", lambda c: c[0])
        self.hostname = self._protected_parse("hostname", lambda c: c[0])
        self.uname = self._protected_parse("uname", lambda c: Uname(c[0]), None)

    def _protected_parse(self, sym_name, parser, default=""):
        try:
            return parser(self.spec_mapper.get_content(sym_name))
        except:
            return default

    def _pull_md_fragment(self):
        hn = self.get_contextual_hostname()
        sub_systems = [s for s in self.archive_metadata["systems"] if s["system_id"] == hn]
        assert len(sub_systems) == 1
        return sub_systems[0]

    def run_mappers(self):
        if self.archive_metadata:
            md = self.run_metadata_mappers(self._pull_md_fragment())
            self.mapper_results.update(md)
        for symbolic_name, files in self.spec_mapper.symbolic_files.items():
            for f in files:
                content = self.spec_mapper.get_content(f, symbolic=False)
                if len(content) == 1 and content[0] == "Command not found":
                    continue
                for plugin in plugins.get_mappers(symbolic_name):
                    context = self.build_context(content=content, path=f)
                    try:
                        self.add_result(plugin(context), symbolic_name, plugin)
                    except Exception as e:
                        self.handle_map_error(e, context)

    def get_response(self):
        return self.format_response({
            "system": {
                "metadata": self.metadata,
                "hostname": self.hostname
            },
            "reports": self.reducer_results
        })

    def _marshal(self, result, symbolic_name, shared):
        if shared:
            return result
        else:
            use_value_list = self.is_pattern_file(symbolic_name)
            return marshaller.marshal(result, use_value_list=use_value_list)

    def add_result(self, r, symbolic_name, plugin):
        if r is not None:
            r = self._marshal(r, symbolic_name, plugin.shared)
            self.mapper_results[plugin].append(r)

    def handle_result(self, r, plugin):
        validate_response(r)
        type_ = r["type"]
        del r["type"]
        if type_ == "metadata":
            self.append_metadata(r)
        elif type_ == "rule":
            self.reducer_results.append(self.format_result({
                "rule_id": "{0}|{1}".format(plugins.get_name(plugin), r["error_key"]),
                "details": r
            }))

    def run_reducers(self):
        generator = reducer.run_host(
            self.mapper_results, self.handle_reducer_error())
        for plugin, r in generator:
            self.handle_result(r, plugin)


class MultiEvaluator(Evaluator):

    def __init__(self, spec_mapper, metadata=None):
        super(MultiEvaluator, self).__init__(spec_mapper)
        self.mapper_results = {}
        self.SubEvaluator = self.sub_evaluator_class()
        self.archive_results = defaultdict(lambda: {
            "system": {
                "metadata": {}
            },
            "reports": []
        })
        self.archive_results[None]["system"]["type"] = "cluster"
        if metadata:
            self.archive_metadata = metadata
        else:
            md_str = spec_mapper.get_content("metadata.json", split=False, default="{}")
            self.archive_metadata = marshalling.unmarshal(md_str)

    def sub_evaluator_class(self):
        return SingleEvaluator

    def run_mappers(self, **kwargs):
        self.mapper_results[None] = self.run_metadata_mappers(self.archive_metadata)
        subarchives = [a for a in self.spec_mapper.tf.getnames() if a.endswith(".tar")]
        for i, archive in enumerate(subarchives):
            content = self.spec_mapper.get_content(archive, split=False, symbolic=False)
            extractor = archives.InMemoryExtractor().from_buffer(content)
            sub_spec_mapper = specs.SpecMapper(extractor)
            sub_evaluator = self.SubEvaluator(sub_spec_mapper, metadata=self.archive_metadata)
            host_result = sub_evaluator.process()
            hn = sub_evaluator.get_contextual_hostname(default=i)
            self.archive_results[hn] = host_result
            self.mapper_results[hn] = sub_evaluator.mapper_results

    def run_reducers(self, metadata=None):
        generator = reducer.run_multi(self.mapper_results, self.handle_reducer_error())
        for plugin, r in generator:
            self.handle_result(r, plugin)

    def handle_result(self, r, plugin):
        validate_response(r)
        type_ = r["type"]
        del r["type"]
        if type_ == "metadata":
            self.append_metadata(r)
        elif type_ == "rule":
            self.archive_results[None]["reports"].append(self.format_result({
                "rule_id": "{0}|{1}".format(plugins.get_name(plugin), r["error_key"]),
                "details": r
            }))

    def append_metadata(self, r):
        for k, v in r.iteritems():
            self.archive_results[None]["system"]["metadata"][k] = v

    def get_response(self):
        return self.format_response({
            "system": self.archive_results[None]["system"],
            "reports": self.archive_results[None]["reports"],
            "archives": [v for k, v in self.archive_results.iteritems() if k is not None]
        })


class InsightsEvaluator(SingleEvaluator):

    def __init__(self, spec_mapping, url="not set", system_id=None, metadata=None):
        super(InsightsEvaluator, self).__init__(spec_mapping, metadata=metadata)
        self.system_id = system_id
        self.url = url

    def format_result(self, result):
        result["system_id"] = self.system_id
        return result

    def get_contextual_hostname(self, default=""):
        return self.system_id

    def set_branch_info(self, system):
        branch_info = json.loads(self.spec_mapper.get_content("branch_info",
                                 split=False, default="{}"))
        remote_branch = branch_info.get("remote_branch")
        if remote_branch == -1:
            remote_branch = None
        remote_leaf = branch_info.get("remote_leaf")
        if remote_leaf == -1:
            remote_leaf = None
        system["remote_branch"] = remote_branch
        system["remote_leaf"] = remote_leaf

    def pre_mapping(self):
        super(InsightsEvaluator, self).pre_mapping()
        int_system_id = self.spec_mapper.get_content("machine-id")[0]
        if self.system_id and self.system_id != int_system_id:
            raise InvalidArchive("Given system_id does not match archive: %s" % int_system_id)
        self.system_id = int_system_id

    def format_response(self, response):
        response["system"]["system_id"] = self.system_id
        if self.release:
            response["system"]["metadata"]["release"] = self.release
        response["system"]["type"] = "host"
        response["system"]["product"] = "rhel"
        self.set_branch_info(response["system"])
        return response

    def handle_map_error(self, e, context):
        log.warning("Mapper failed with message %s. Ignoring. context: %s [%s]",
                    e, context, self.url, exc_info=True)

    def handle_reduce_error(self, e, context):
        log.warning("Reducer failed with message %s. Ignoring. context: %s [%s]",
                    e, context, self.url, exc_info=True)


class InsightsMultiEvaluator(MultiEvaluator):

    def __init__(self, spec_mapper, system_id=None, metadata=None):
        super(InsightsMultiEvaluator, self).__init__(spec_mapper, metadata=metadata)
        self.system_id = system_id

    def pre_mapping(self):
        super(InsightsMultiEvaluator, self).pre_mapping()
        int_system_id = self.archive_metadata.get("system_id", "")
        if self.system_id and self.system_id != int_system_id:
            raise InvalidArchive("Given system_id does not match archive: %s" % int_system_id)
        self.system_id = int_system_id

    def sub_evaluator_class(self):
        return InsightsEvaluator

    def format_result(self, result):
        result["system_id"] = self.system_id
        return result

    def format_response(self, response):
        response["system"]["system_id"] = self.system_id
        product = self.archive_metadata.get("product", "machine")
        response["system"]["product"] = product
        response["system"]["display_name"] = self.archive_metadata.get("display_name", "")
        self.apply_system_metadata(self.archive_metadata["systems"], response)

        # hackhackhackhack
        system_id_hostname_map = {}

        for archive in response["archives"]:
            archive["system"]["product"] = product
            self.hack_report_ids(archive)
            system_id_hostname_map[archive["system"]["system_id"]] = archive["system"]["hostname"]

        self.hack_affected_hosts(system_id_hostname_map, response)
        for key in ["systems", "system_id", "product", "display_name"]:
            del self.archive_metadata[key]
        response["system"]["metadata"] = self.archive_metadata
        return response

    def hack_affected_hosts(self, mapping, response):
        for report in response["reports"]:
            if "affected_hosts" in report["details"]:
                new_hosts = [mapping[h] for h in report["details"]["affected_hosts"]]
                report["details"]["affected_hosts"] = new_hosts
                report["details"]["hostname_mapping"] = mapping

    def hack_report_ids(self, archive):
        archive_type = archive["system"]["type"]
        product = archive["system"]["product"]
        if archive_type in ["Hypervisor", "image", "container"]:
            for report in archive["reports"]:
                report["rule_id"] += "#" + ".".join([product, archive_type])

    def apply_system_metadata(self, system_metadata, response):
        for system_md in system_metadata:
            system_id = system_md.pop("system_id")
            for system in response["archives"]:
                if system["system"]["system_id"] == system_id:
                    system["system"].update(system_md)
                    break
