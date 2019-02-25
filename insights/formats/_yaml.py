import yaml
import sys

from insights.core.evaluators import SingleEvaluator
from insights.formats import EvaluatorFormatterAdapter


class YamlFormat(SingleEvaluator):
    def postprocess(self):
        yaml.dump(self.get_response(), self.stream)


class YamlFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = YamlFormat

    @staticmethod
    def configure(p):
        p.add_argument("-F", "--fail-only", help="Show FAIL results only. Conflict with '-m' or '-f', will be dropped when using them together", action="store_true")

    def __init__(self, args):
        super(YamlFormatterAdapter, self).__init__(args)
        if args.fail_only:
            print('Options conflict: -f and -F, drops -F', file=sys.stderr)
