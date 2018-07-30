import yaml

from insights.formats import EvaluatorFormatter


class YamlFormatter(EvaluatorFormatter):
    def dump(self, data):
        return yaml.dump(data)
