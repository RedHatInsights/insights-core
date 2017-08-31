import json
from collections import defaultdict

from insights.core import archives, specs, marshalling, plugins
from insights.core.marshalling import Marshaller
from insights.core.plugins import validate_response, stringify_requirements
from insights.core.context import Context
from insights.core.archives import InvalidArchive
from insights.parsers.uname import Uname
from insights.core import reducer
from datetime import datetime

import logging
log = logging.getLogger("eval")

marshaller = Marshaller()


def name_from_module(plugin):
    return plugin.__name__.rpartition(".")[-1]


def serialize_skips(skips):
    for skip in skips:
        skip["details"] = stringify_requirements(skip["details"])


class Evaluator(object):

    def is_pattern_file(self, symbolic_name):
        return self.spec_mapper.data_spec_config.is_multi_output(symbolic_name)

    def __init__(self, spec_mapper, metadata=None):
        self.spec_mapper = spec_mapper
        self.metadata = defaultdict(dict)
        self.rule_skips = []
        self.rule_results = []
        self.archive_metadata = metadata
        self.stats = self._init_stats()

    def _init_stats(self):
        return {
            "parser": {"count": 0, "fail": 0},
            "reducer": {"count": 0, "fail": 0},
            "skips": {"count": 0}
        }

    def pre_mapping(self):
        pass

    def format_response(self, response):
        """
        To be overridden by subclasses to format the response sent back to the
        client.
        """
        return response

    def format_result(self, result):
        """
        To be overridden by subclasses to format individual rule results.
        """
        return result

    def handle_reducer_error(self):
        self.stats["reducer"]["fail"] += 1

        def default_error_handler(func, e, local, shared):
            log.exception("Reducer [%s] failed", ".".join([func.__module__, func.__name__]))
        return default_error_handler

    def get_contextual_hostname(self, default=""):
        return self.hostname if hasattr(self, "hostname") and self.hostname else default

    def _execute_parser(self, parser, context):
        self.stats["parser"]["count"] += 1
        return parser(context)

    def run_metadata_parsers(self, the_meta_data):
        """
        Special case of running the parser for metadata.json.  This is special
        because metadata.json is the only file not contained in an individual
        Insights archive.
        """
        MD_JSON = "metadata.json"
        result_map = {}
        for plugin in plugins.get_parsers(MD_JSON):
            context = self.build_context(content=marshalling.marshal(the_meta_data).splitlines(),
                                         path=MD_JSON,
                                         target=MD_JSON)
            try:
                result = self._execute_parser(plugin, context)
                if result:
                    result_map[plugin] = [result]
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
        if hasattr(self, "last_client_run"):
            kwargs["last_client_run"] = self.last_client_run
        if self.archive_metadata:
            kwargs["metadata"] = self.archive_metadata
        return Context(**kwargs)

    def process(self):
        self.pre_mapping()
        self.run_parsers()
        self.run_reducers()
        self.post_process()
        return self.get_response()

    def post_process(self):
        pass

    def handle_map_error(self, e, context):
        self.stats["parser"]["fail"] += 1
        log.exception("Parser failed")

    def handle_content_error(self, e, filename):
        log.exception("Unable to extract content from %s.", filename)


class SingleEvaluator(Evaluator):

    def __init__(self, spec_mapper, metadata=None):
        super(SingleEvaluator, self).__init__(spec_mapper, metadata)
        self.parser_results = defaultdict(list)

    def append_metadata(self, r, plugin):
        for k, v in r.iteritems():
            self.metadata[k] = v

    def pre_mapping(self):
        self.release = self._protected_parse("redhat-release", lambda c: c[0])
        self.hostname = self._protected_parse("hostname", lambda c: c[0], default=None)
        if self.hostname is None:
            self.hostname = self._protected_parse("facts", lambda c: [x.split()[-1] for x in c if x.startswith('fqdn')][0])
        self.uname = self._protected_parse("uname", lambda c: Uname(c[0]), None)
        self.calc_last_client_run()

    def calc_last_client_run(self):
        content = self.spec_mapper.get_content("prev_uploader_log")
        if content and len(content) > 1:
            date_str = " ".join(content[0:1]).split(",")[0]
            self.last_client_run = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    def format_response(self, response):
        serialize_skips(response["skips"])
        response["stats"]["skips"]["count"] = len(self.rule_skips)
        return response

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

    def run_parsers(self):
        if self.archive_metadata:
            md = self.run_metadata_parsers(self._pull_md_fragment())
            self.parser_results.update(md)
        for symbolic_name, files in self.spec_mapper.symbolic_files.items():

            if not plugins.get_parsers(symbolic_name):
                continue

            for f in files:
                content = []
                try:
                    content = self.spec_mapper.get_content(f, symbolic=False)
                except Exception as e:
                    self.handle_content_error(e, f)
                    continue

                cmd_not_found_list = ["Command not found", "timeout: failed to run command"]
                if len(content) == 1 and any([cmd_without in content[0] for cmd_without in cmd_not_found_list]):
                    continue
                for plugin in plugins.get_parsers(symbolic_name):
                    unrooted_path = f.split(self.spec_mapper.root)[1].lstrip("/")
                    context = self.build_context(content=content,
                                                 path=unrooted_path,
                                                 target=symbolic_name)
                    try:
                        self.add_result(self._execute_parser(plugin, context),
                                        symbolic_name, plugin)
                    except Exception as e:
                        self.handle_map_error(e, context)

    def get_response(self):
        return self.format_response({
            "system": {
                "metadata": self.metadata,
                "hostname": self.hostname
            },
            "reports": self.rule_results,
            "skips": self.rule_skips,
            "stats": self.stats
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
            self.parser_results[plugin].append(r)

    def handle_result(self, plugin, r):
        validate_response(r)
        type_ = r["type"]
        del r["type"]
        if type_ == "metadata":
            self.append_metadata(r, plugin)
        elif type_ == "rule":
            self.rule_results.append(self.format_result({
                "rule_id": "{0}|{1}".format(plugins.get_name(plugin), r["error_key"]),
                "details": r
            }))
        elif type_ == "skip":
            self.rule_skips.append(r)

    def run_reducers(self):
        self.all_output = {}
        generator = reducer.run_host(
            self.parser_results,
            self.all_output,
            self.handle_reducer_error(),
            reducer_stats=self.stats['reducer'])
        for plugin, r in generator:
            self.handle_result(plugin, r)


class MultiEvaluator(Evaluator):

    def __init__(self, spec_mapper, metadata=None):
        super(MultiEvaluator, self).__init__(spec_mapper)
        self.parser_results = {}
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

    def run_parsers(self, **kwargs):
        self.parser_results[None] = self.run_metadata_parsers(self.archive_metadata)
        subarchives = [a for a in self.spec_mapper.tf.getnames() if a.endswith(".tar")]
        for i, archive in enumerate(subarchives):
            content = self.spec_mapper.get_content(archive, split=False, symbolic=False)
            extractor = archives.TarExtractor().from_buffer(content)
            sub_spec_mapper = specs.SpecMapper(extractor)
            sub_evaluator = self.SubEvaluator(sub_spec_mapper, metadata=self.archive_metadata)
            host_result = sub_evaluator.process()
            hn = sub_evaluator.get_contextual_hostname(default=i)
            self.archive_results[hn] = host_result
            self.parser_results[hn] = sub_evaluator.parser_results

    def run_reducers(self, metadata=None):
        self.all_output = {}
        generator = reducer.run_multi(
            self.parser_results,
            self.all_output,
            self.handle_reducer_error(),
            reducer_stats=self.stats['reducer'])
        for plugin, r in generator:
            self.handle_result(plugin, r)

    def handle_result(self, plugin, r):
        validate_response(r)
        type_ = r["type"]
        del r["type"]
        if type_ == "metadata":
            self.append_metadata(r, plugin)
        elif type_ == "rule":
            self.archive_results[None]["reports"].append(self.format_result({
                "rule_id": "{0}|{1}".format(plugins.get_name(plugin), r["error_key"]),
                "details": r
            }))
        elif type_ == "skip":
            self.rule_skips.append(r)

    def append_metadata(self, r, plugin):
        for k, v in r.iteritems():
            self.archive_results[None]["system"]["metadata"][k] = v

    def get_response(self):
        return self.format_response({
            "system": self.archive_results[None]["system"],
            "reports": self.archive_results[None]["reports"],
            "archives": [v for k, v in self.archive_results.iteritems() if k is not None],
            "skips": self.rule_skips,
            "stats": self.stats
        })


class InsightsEvaluator(SingleEvaluator):

    def __init__(self, spec_mapper, url="not set", system_id=None, metadata=None):
        super(InsightsEvaluator, self).__init__(spec_mapper, metadata=metadata)
        self.system_id = system_id
        self.url = url

    def format_result(self, result):
        result["system_id"] = self.system_id
        return result

    def get_contextual_hostname(self, default=""):
        return self.system_id

    def get_branch_info(self):
        version = None
        hostname = None
        branch_info = json.loads(self.spec_mapper.get_content("branch_info",
                                 split=False, default="{}"))
        product = branch_info.get("product")
        remote_branch = branch_info.get("remote_branch")
        if remote_branch == -1:
            remote_branch = None
        remote_leaf = branch_info.get("remote_leaf")
        if remote_leaf == -1:
            remote_leaf = None
        if hasattr(product, "type") and product["type"] == "Satellite":
            version = "{}.{}".format(product["major_version"], product["minor_version"])
            hostname = branch_info.get("hostname")

        return {
            'remote_branch': remote_branch,
            'remote_leaf': remote_leaf,
            'metadata': {
                'satellite_information': {
                    'version': version,
                    'hostname': hostname
                }
            }
        }

    def get_product_info(self):
        md = json.loads(self.spec_mapper.get_content("metadata.json",
                        split=False, default="{}"))
        return md.get("product_code", "rhel"), md.get("role", "host")

    def pre_mapping(self):
        super(InsightsEvaluator, self).pre_mapping()
        int_system_id = self.spec_mapper.get_content("machine-id")[0]
        if self.system_id and self.system_id != int_system_id:
            raise InvalidArchive("Given system_id does not match archive: %s" % int_system_id)
        self.system_id = int_system_id

    def format_response(self, response):
        serialize_skips(response["skips"])
        system = response["system"]
        branch_info = self.get_branch_info()
        system['metadata'].update(branch_info['metadata'])
        system['remote_branch'] = branch_info['remote_branch']
        system['remote_leaf'] = branch_info['remote_leaf']
        system["system_id"] = self.system_id
        if self.release:
            system["metadata"]["release"] = self.release
        system["product"], system["type"] = self.get_product_info()
        response["stats"]["skips"]["count"] = len(self.rule_skips)

        return response

    def handle_content_error(self, e, filename):
        log.warning("Unable to extract content from %s [%s]. Failed with message %s. Ignoring.",
                    filename, self.url, e, exc_info=True)

    def handle_map_error(self, e, context):
        self.stats["parser"]["fail"] += 1
        log.warning("Parser failed with message %s. Ignoring.",
                    e, context, exc_info=True, extra={
                        "context": context,
                        "url": self.url,
                        "exception_message": str(e)
                    })

    def handle_reduce_error(self, e, context):
        self.stats["reducer"]["fail"] += 1
        log.warning("Reducer failed with message %s. Ignoring.",
                    e, exc_info=True, extra={
                        "context": context,
                        "url": self.url,
                        "exception_message": str(e)
                    })


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
        serialize_skips(response["skips"])
        response["system"]["system_id"] = self.system_id
        product = self.archive_metadata.get("product", "machine")
        response["system"]["product"] = product
        response["system"]["display_name"] = self.archive_metadata.get("display_name", "")
        self.apply_system_metadata(self.archive_metadata["systems"], response)

        # hackhackhackhack
        system_id_hostname_map = {}

        for archive in response["archives"]:
            archive["system"]["product"] = product
            system_id_hostname_map[archive["system"]["system_id"]] = archive["system"]["hostname"]

        self.hack_affected_hosts(system_id_hostname_map, response)
        for key in ["systems", "system_id", "product", "display_name"]:
            del self.archive_metadata[key]
        response["system"]["metadata"] = self.archive_metadata
        response["stats"]["skips"]["count"] = len(self.rule_skips)
        return response

    def hack_affected_hosts(self, mapping, response):
        for report in response["reports"]:
            if "affected_hosts" in report["details"]:
                new_hosts = [mapping[h] for h in report["details"]["affected_hosts"]]
                report["details"]["affected_hosts"] = new_hosts
                report["details"]["hostname_mapping"] = mapping

    def apply_system_metadata(self, system_metadata, response):
        for system_md in system_metadata:
            system_id = system_md.pop("system_id")
            for system in response["archives"]:
                if system["system"]["system_id"] == system_id:
                    system["system"].update(system_md)
                    break
