import json

from insights.formats import EvaluatorFormatterAdapter, EvaluatorFormatter


class JsonFormatter(EvaluatorFormatter):
    def dump(self, data):
        return json.dumps(data)


class JsonFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = JsonFormatter
