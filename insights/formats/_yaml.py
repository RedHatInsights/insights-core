import yaml

from insights.core.evaluators import SingleEvaluator
from insights.formats import EvaluatorFormatterAdapter
from yaml.representer import Representer
from insights.core import ScanMeta

Representer.add_representer(ScanMeta, Representer.represent_name)


class YamlFormat(SingleEvaluator):
    def postprocess(self):
        yaml.dump(self.get_response(), self.stream)


class YamlFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = YamlFormat
