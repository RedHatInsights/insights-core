import yaml

from insights.formats import EvaluatorFormatterAdapter, EvaluatorFormatter


class YamlFormat(EvaluatorFormatter):
    def dump(self, data):
        return yaml.dump(data)


class YamlFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = YamlFormat
