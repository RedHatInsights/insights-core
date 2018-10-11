import yaml

from insights.core.evaluators import SingleEvaluator
from insights.formats import EvaluatorFormatterAdapter


class YamlFormat(SingleEvaluator):
    def postprocess(self):
        yaml.dump(self.get_response(), self.stream)


class YamlFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = YamlFormat
