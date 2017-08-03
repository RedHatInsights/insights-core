import json
import logging
from collections import defaultdict

from insights.core import dr
from insights.core import marshalling, plugins
from insights.core.dr import stringify_requirements
from insights.core.context import Context
from insights.core.archives import InvalidArchive

log = logging.getLogger(__name__)


def get_simple_module_name(obj):
    return dr.BASE_MODULE_NAMES.get(obj, None)


def serialize_skips(skips):
    for skip in skips:
        skip["details"] = stringify_requirements(skip["details"])


class Evaluator(object):

    def is_pattern_file(self, symbolic_name):
        return self.spec_mapper.data_spec_config.is_multi_output(symbolic_name)

    def __init__(self, spec_mapper, broker=None, metadata=None):
        self.spec_mapper = spec_mapper
        self.broker = broker or dr.Broker()
        self.metadata = defaultdict(dict)
        self.rule_skips = []
        self.rule_results = []
        self.archive_metadata = metadata
        self.stats = self._init_stats()
        self.hostname = None

    def _init_stats(self):
        return {
            "parser": {"count": 0, "fail": 0},
            "rule": {"count": 0, "fail": 0},
            "skips": {"count": 0}
        }

    def pre_process(self):
        pass

    def post_process(self):
        for c, exes in self.broker.exceptions.iteritems():
            for e in exes:
                if plugins.is_parser(c):
                    self.handle_parse_error(c, e)
                elif plugins.is_rule(c):
                    self.handle_rule_error(c, e)

        for c, v in self.broker.instances.iteritems():
            if plugins.is_rule(c):
                self.handle_result(c, v)

    def run_components(self):
        dr.run(dr.COMPONENTS[dr.GROUPS.single], broker=self.broker)

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

    def get_contextual_hostname(self, default=""):
        return self.hostname or default

    def process(self):
        self.pre_process()
        self.run_components()
        self.post_process()
        return self.get_response()

    def handle_parse_error(self, parser, exception):
        self.stats["parser"]["fail"] += 1
        log.exception("Parser failed")

    def handle_rule_error(self, rule, exception):
        self.stats["rule"]["fail"] += 1

    def handle_content_error(self, e, filename):
        log.exception("Unable to extract content from %s.", filename)


class SingleEvaluator(Evaluator):

    def __init__(self, spec_mapper, broker=None, metadata=None):
        super(SingleEvaluator, self).__init__(spec_mapper, broker, metadata)

    def append_metadata(self, r, plugin):
        for k, v in r.iteritems():
            self.metadata[k] = v

    def format_response(self, response):
        serialize_skips(response["skips"])
        response["stats"]["skips"]["count"] = len(self.rule_skips)
        return response

    def _protected_parse(self, sym_name, parser, default=""):
        try:
            data = self.spec_mapper.get_content(sym_name)
            result = parser(data)
            return result
        except:
            return default

    def _pull_md_fragment(self):
        hn = self.machine_id
        sub_systems = [s for s in self.archive_metadata["systems"] if s["system_id"] == hn]
        assert len(sub_systems) == 1
        return sub_systems[0]

    def pre_process(self):
        self.release = self._protected_parse("redhat-release", lambda c: c[0], default=None)
        self.machine_id = self._protected_parse("machine-id", lambda c: c[0], default=None)
        self.hostname = self._protected_parse("hostname", lambda c: c[0], default=None)
        if self.hostname is None:
            self.hostname = self._protected_parse("facts", lambda c: [x.split()[-1] for x in c if x.startswith('fqdn')][0])

        if self.archive_metadata:
            self.broker["metadata.json"] = self._pull_md_fragment()

        for symbolic_name, files in self.spec_mapper.symbolic_files.iteritems():
            if symbolic_name == "metadata.json":
                continue

            is_pattern = self.is_pattern_file(symbolic_name)
            if not is_pattern and len(files) > 1:
                raise Exception("Multiple files for simple file spec: %s" % symbolic_name)

            if is_pattern:
                self.broker[symbolic_name] = []

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

                unrooted_path = f.split(self.spec_mapper.root)[1].lstrip("/")
                hn = self.get_contextual_hostname()
                context = Context(content=content, path=unrooted_path, target=symbolic_name, hostname=hn)
                if is_pattern:
                    self.broker[symbolic_name].append(context)
                else:
                    self.broker[symbolic_name] = context

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

    def handle_result(self, plugin, r):
        type_ = r["type"]
        if type_ == "metadata":
            self.append_metadata(r, plugin)
        elif type_ == "rule":
            self.rule_results.append(self.format_result({
                "rule_id": "{0}|{1}".format(get_simple_module_name(plugin), r["error_key"]),
                "details": r
            }))
        elif type_ == "skip":
            self.rule_skips.append(r)


class MultiEvaluator(Evaluator):

    def __init__(self, spec_mapper, broker=None, metadata=None):
        super(MultiEvaluator, self).__init__(spec_mapper)
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

    def clean_broker(self, broker):
        for c in [d for d in broker.keys() if not plugins.is_component(d)]:
            del broker[c]
        return broker

    def pre_process(self):
        sub_brokers = {}
        for i, sub_spec_mapper in enumerate(self.spec_mapper.sub_spec_mappers()):
            sub_evaluator = self.SubEvaluator(sub_spec_mapper, metadata=self.archive_metadata)
            host_result = sub_evaluator.process()
            hn = sub_evaluator.get_contextual_hostname(default=i)
            self.archive_results[hn] = host_result
            sub_brokers[hn] = self.clean_broker(sub_evaluator.broker)
        for host, sub in sub_brokers.iteritems():
            for c, v in sub.instances.iteritems():
                if plugins.is_rule(c):
                    continue
                if c not in self.broker:
                    self.broker[c] = {}
                self.broker[c][host] = v
        self.broker["metadata.json"] = self.archive_metadata

    def run_components(self):
        dr.run(dr.COMPONENTS[dr.GROUPS.cluster], broker=self.broker)

    def handle_result(self, plugin, r):
        type_ = r["type"]
        if type_ == "metadata":
            self.append_metadata(r, plugin)
        elif type_ == "rule":
            self.archive_results[None]["reports"].append(self.format_result({
                "rule_id": "{0}|{1}".format(get_simple_module_name(plugin), r["error_key"]),
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

    def __init__(self, spec_mapper, broker=None, url="not set", system_id=None, metadata=None):
        super(InsightsEvaluator, self).__init__(spec_mapper, broker, metadata=metadata)
        self.system_id = system_id
        self.url = url

    def format_result(self, result):
        result["system_id"] = self.system_id
        return result

    def get_contextual_hostname(self, default=""):
        return self.system_id or default

    def get_branch_info(self):
        version = hostname = None
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

    def pre_process(self):
        int_system_id = self.spec_mapper.get_content("machine-id")[0]
        if self.system_id and self.system_id != int_system_id:
            raise InvalidArchive("Given system_id does not match archive: %s" % int_system_id)
        self.system_id = int_system_id
        super(InsightsEvaluator, self).pre_process()

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

    def handle_parse_error(self, component, exception):
        context = self.broker.get(dr.get_dependencies(component).pop(), "Unknown")
        self.stats["parser"]["fail"] += 1
        log.warning("Parser failed with message %s. Ignoring. context: %s [%s]",
                    exception, context, self.url, exc_info=True)


class InsightsMultiEvaluator(MultiEvaluator):

    def __init__(self, spec_mapper, broker=None, system_id=None, metadata=None):
        super(InsightsMultiEvaluator, self).__init__(spec_mapper, broker=broker, metadata=metadata)
        self.system_id = system_id

    def pre_process(self):
        super(InsightsMultiEvaluator, self).pre_process()
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
