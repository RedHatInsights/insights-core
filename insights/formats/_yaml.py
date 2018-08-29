import yaml

from insights.formats import EvaluatorFormatterAdapter, EvaluatorFormatter


class YamlFormatter(EvaluatorFormatter):
    def dump(self, data):
        return yaml.dump(data)


class YamlFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = YamlFormatter
