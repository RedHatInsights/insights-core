import yaml
import sys

from insights.core.evaluators import SingleEvaluator
from insights.formats import EvaluatorFormatterAdapter, get_response_of_types
from yaml.representer import Representer
from insights.core import ScanMeta

Representer.add_representer(ScanMeta, Representer.represent_name)


class YamlFormat(SingleEvaluator):
    def __init__(self,
            broker=None,
            missing=False,
            show_rules=None,
            stream=sys.stdout):
        super(YamlFormat, self).__init__(broker, stream=stream)
        self.missing = missing
        self.show_rules = [] if show_rules is None else show_rules

    def postprocess(self):
        response = get_response_of_types(self.get_response(), self.missing, self.show_rules)
        yaml.dump(response, self.stream)


class YamlFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = YamlFormat
