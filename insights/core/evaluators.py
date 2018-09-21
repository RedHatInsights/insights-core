import logging
import sys

from ..formats import Formatter
from ..specs import Specs
from ..combiners.hostname import hostname as combiner_hostname
from ..parsers.branch_info import BranchInfo
from . import dr, plugins

log = logging.getLogger(__name__)


def get_simple_module_name(obj):
    return dr.BASE_MODULE_NAMES.get(obj, None)


class Evaluator(Formatter):
    def __init__(self, broker=None, stream=sys.stdout, incremental=False):
        super(Evaluator, self).__init__(broker or dr.Broker(), stream)
        self.rule_skips = []
        self.rule_results = []
        self.fingerprint_results = []
        self.hostname = None
        self.metadata = {}
        self.metadata_keys = {}
        self.incremental = incremental

    def observer(self, comp, broker):
        if comp is combiner_hostname and comp in broker:
            self.hostname = broker[comp].fqdn

        if plugins.is_rule(comp) and comp in broker:
            self.handle_result(comp, broker[comp])

    def preprocess(self):
        self.broker.add_observer(self.observer)

    def run_serial(self, graph=None):
        dr.run(graph or dr.COMPONENTS[dr.GROUPS.single], broker=self.broker)

    def run_incremental(self, graph=None):
        for _ in dr.run_incremental(graph or dr.COMPONENTS[dr.GROUPS.single], broker=self.broker):
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

    def process(self, graph=None):
        with self:
            if self.incremental:
                self.run_incremental(graph)
            else:
                self.run_serial(graph)
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
    def __init__(self, broker=None, system_id=None, stream=sys.stdout, incremental=False):
        super(InsightsEvaluator, self).__init__(broker, stream=sys.stdout, incremental=incremental)
        self.system_id = system_id
        self.branch_info = {}
        self.product = "rhel"
        self.type = "host"
        self.release = None

    def observer(self, comp, broker):
        super(InsightsEvaluator, self).observer(comp, broker)
        if comp is Specs.machine_id and comp in broker:
            self.system_id = broker[Specs.machine_id].content[0].strip()

        if comp is Specs.redhat_release and comp in broker:
            self.release = broker[comp].content[0].strip()

        if comp is BranchInfo and BranchInfo in broker:
            self.branch_info = broker[comp].data

        if comp is Specs.metadata_json and comp in broker:
            md = broker[comp]
            self.product = md.get("product_code")
            self.type = md.get("role")

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
