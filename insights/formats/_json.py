import json

from insights.formats import EvaluatorFormatterAdapter, EvaluatorFormatter


class JsonFormat(EvaluatorFormatter):
    def dump(self, data):
        return json.dumps(data)


class JsonFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = JsonFormat
