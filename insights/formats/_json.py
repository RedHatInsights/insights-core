import json

from insights.core.evaluators import SingleEvaluator
from insights.formats import EvaluatorFormatterAdapter


class JsonFormat(SingleEvaluator):
    def postprocess(self):
        json.dump(self.get_response(), self.stream)


class JsonFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = JsonFormat
