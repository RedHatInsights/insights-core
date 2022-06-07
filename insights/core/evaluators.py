import logging
import six
import sys

from collections import defaultdict
from datetime import datetime

from ..formats import Formatter
from ..specs import Specs
from ..combiners.hostname import Hostname as combiner_hostname
from ..parsers.branch_info import BranchInfo
from ..util import utc
from . import dr, plugins
from .context import ExecutionContext
import insights

log = logging.getLogger(__name__)


def get_simple_module_name(obj):
    return dr.BASE_MODULE_NAMES.get(obj, None)


class Evaluator(Formatter):
    def __init__(self, broker=None, stream=sys.stdout, incremental=False):
        super(Evaluator, self).__init__(broker or dr.Broker(), stream)
        self.results = defaultdict(list)
        self.rule_skips = []
        self.hostname = None
        self.metadata = {}
        self.metadata_keys = {}
        self.incremental = incremental
        self.context_cls = None

    def observer(self, comp, broker):
        if self.context_cls is None:
            for c in self.broker.instances:
                try:
                    if issubclass(c, ExecutionContext):
                        self.context_cls = c
                except:
                    pass

        if comp is combiner_hostname and comp in broker:
            self.hostname = broker[comp].fqdn

        if plugins.is_rule(comp) and comp in broker:
            self.handle_result(comp, broker[comp])

    def preprocess(self):
        self.broker.add_observer(self.observer)

    def run_serial(self, graph=None):
        dr.run(graph or dr.COMPONENTS[dr.GROUPS.single], broker=self.broker)

    def run_incremental(self, graph=None, parallel=False):
        components = graph or dr.COMPONENTS[dr.GROUPS.single]
        if parallel:
            with insights.get_pool(parallel, "insights-engine-pool", {"max_workers": None}) as pool:
                dr.run_all(components, self.broker, pool)
        else:
            dr.run_all(components, self.broker)

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

    def process(self, graph=None, parallel=False):
        with self:
            if self.incremental:
                self.run_incremental(graph, parallel)
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
            "reports": self.results["rule"],
            "fingerprints": self.results["fingerprint"],
            "skips": self.rule_skips,
        })

        for k, v in six.iteritems(self.results):
            if k not in ("rule", "fingerprint"):
                r[k] = v

        r = self.format_response(r)

        ctx = dr.get_name(self.context_cls) if self.context_cls is not None else None

        r["analysis_metadata"] = {
            "start": self.start_time.isoformat(),
            "finish": datetime.now(utc).isoformat(),
            "execution_context": ctx,
            "plugin_sets": insights.RULES_STATUS
        }

        return r

    def handle_result(self, plugin, r):
        type_ = r["type"]

        if type_ == "skip":
            self.rule_skips.append(r)
        elif type_ == "metadata":
            self.append_metadata(r)
        elif type_ == "metadata_key":
            self.metadata_keys[r.get_key()] = r["value"]
        else:
            response_id = "%s_id" % r.response_type
            key = r.get_key()
            self.results[type_].append(self.format_result({
                response_id: "{0}|{1}".format(get_simple_module_name(plugin), key),
                "component": dr.get_name(plugin),
                "type": type_,
                "key": key,
                "details": r,
                "tags": list(dr.get_tags(plugin)),
                "links": dr.get_delegate(plugin).links or {}
            }))


class InsightsEvaluator(SingleEvaluator):
    def __init__(self, broker=None, system_id=None, stream=sys.stdout, incremental=False):
        super(InsightsEvaluator, self).__init__(broker, stream=stream, incremental=incremental)
        self.system_id = system_id
        self.branch_info = {}
        self.product = "rhel"
        self.type = "host"
        self.release = None

    def observer(self, comp, broker):
        super(InsightsEvaluator, self).observer(comp, broker)
        if self.system_id is None and Specs.machine_id in broker:
            self.system_id = broker[Specs.machine_id].content[0].strip()

        if self.release is None and Specs.redhat_release in broker:
            self.release = broker[Specs.redhat_release].content[0].strip()

        if not self.branch_info and BranchInfo in broker:
            self.branch_info = broker[BranchInfo].data

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
