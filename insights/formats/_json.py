import json
import sys

from insights.core.evaluators import SingleEvaluator as Evaluator
from insights.formats import EvaluatorFormatterAdapter, get_response_of_types


class JsonFormat(Evaluator):
    def __init__(self,
            broker=None,
            missing=False,
            show_rules=None,
            stream=sys.stdout):
        super(JsonFormat, self).__init__(broker, stream=stream)
        self.missing = missing
        self.show_rules = [] if show_rules is None else show_rules

    def postprocess(self):
        response = get_response_of_types(self.get_response(), self.missing, self.show_rules)
        json.dump(response, self.stream)


class JsonFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = JsonFormat
