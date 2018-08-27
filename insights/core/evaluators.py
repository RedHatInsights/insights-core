import logging

from insights import combiners, parsers, specs
from insights.core import dr, plugins

log = logging.getLogger(__name__)


def get_simple_module_name(obj):
    return dr.BASE_MODULE_NAMES.get(obj, None)


class Evaluator(object):

    def __init__(self, broker=None):
        self.broker = broker
        self.rule_skips = []
        self.rule_results = []
        self.fingerprint_results = []
        self.hostname = None
        self.metadata = {}
        self.metadata_keys = {}
        self.release = None

    def pre_process(self):
        pass

    def post_process(self):
        if combiners.hostname.hostname in self.broker:
            self.hostname = self.broker[combiners.hostname.hostname].fqdn

        for p, r in self.broker.items():
            if plugins.is_rule(p):
                self.handle_result(p, r)

    def run_components(self, graph=None):
        dr.run(graph or dr.COMPONENTS[dr.GROUPS.single], broker=self.broker)

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

    def process(self, graph=None):
        self.pre_process()
        self.run_components(graph)
        self.post_process()
        return self.get_response()


class SingleEvaluator(Evaluator):

    def append_metadata(self, r):
        for k, v in r.items():
            if k != "type":
                self.metadata[k] = v

    def format_response(self, response):
        return response

    def get_response(self):
        r = dict(self.metadata_keys)
        r.update({
            "system": {
                "metadata": self.metadata,
                "hostname": self.hostname
            },
            "reports": self.rule_results,
            "fingerprints": self.fingerprint_results,
            "skips": self.rule_skips,
        })
        return self.format_response(r)

    def handle_result(self, plugin, r):
        type_ = r["type"]
        if type_ == "metadata":
            self.append_metadata(r)
        elif type_ == "rule":
            self.rule_results.append(self.format_result({
                "rule_id": "{0}|{1}".format(get_simple_module_name(plugin), r["error_key"]),
                "details": r
            }))
        elif type_ == "fingerprint":
            self.fingerprint_results.append(self.format_result({
                "fingerprint_id": "{0}|{1}".format(get_simple_module_name(plugin), r["fingerprint_key"]),
                "details": r
            }))
        elif type_ == "skip":
            self.rule_skips.append(r)
        elif type_ == "metadata_key":
            self.metadata_keys[r["key"]] = r["value"]


class InsightsEvaluator(SingleEvaluator):

    def __init__(self, broker=None, system_id=None):
        super(InsightsEvaluator, self).__init__(broker)
        self.system_id = system_id
        self.branch_info = None
        self.product = "rhel"
        self.type = "host"

    def post_process(self):
        self.system_id = self.broker[specs.Specs.machine_id].content[0].strip()

        release = self.broker.get(specs.Specs.redhat_release)
        if release:
            self.release = release.content[0].strip()

        branch_info = self.broker.get(parsers.branch_info.BranchInfo)
        self.branch_info = branch_info.data if branch_info else {}

        md = self.broker.get("metadata.json")
        if md:
            self.product = md.get("product_code")
            self.type = md.get("role")

        super(InsightsEvaluator, self).post_process()

    def format_result(self, result):
        result["system_id"] = self.system_id
        return result

    def format_response(self, response):
        system = response["system"]
        system["remote_branch"] = self.branch_info.get("remote_branch")
        system["remote_leaf"] = self.branch_info.get("remote_leaf")
        system["system_id"] = self.system_id
        system["product"] = self.product
        system["type"] = self.type
        if self.release:
            system["metadata"]["release"] = self.release

        return response
