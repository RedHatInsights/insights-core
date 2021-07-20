import json

from insights.core.evaluators import SingleEvaluator as Evaluator
from insights.formats import EvaluatorFormatterAdapter, get_response_of_types


class JsonFormat(Evaluator):
    def __init__(self,
            broker=None,
            missing=False,
            show_rules=None):
        super(JsonFormat, self).__init__(broker)
        self.missing = missing
        self.show_rules = show_rules

    def postprocess(self):
        response = get_response_of_types(self.get_response(), self.missing, self.show_rules)
        json.dump(response, self.stream)


class JsonFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = JsonFormat
