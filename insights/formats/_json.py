import json

from insights.formats import EvaluatorFormatter


class JsonFormatter(EvaluatorFormatter):
    def dump(self, data):
        return json.dumps(data)
