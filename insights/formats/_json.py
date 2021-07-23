import json

from insights.core.evaluators import SingleEvaluator as Evaluator
from insights.formats import EvaluatorFormatterAdapter


class JsonFormat(Evaluator):
    def postprocess(self):
        json.dump(self.get_response(), self.stream)


class JsonFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = JsonFormat
