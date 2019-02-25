import json
import sys

from insights.core.evaluators import SingleEvaluator
from insights.formats import EvaluatorFormatterAdapter


class JsonFormat(SingleEvaluator):
    def postprocess(self):
        json.dump(self.get_response(), self.stream)


class JsonFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = JsonFormat

    @staticmethod
    def configure(p):
        p.add_argument("-F", "--fail-only", help="Show FAIL results only. Conflict with '-m' or '-f', will be dropped when using them together", action="store_true")

    def __init__(self, args):
        super(JsonFormatterAdapter, self).__init__(args)
        if args.fail_only:
            print('Options conflict: -f and -F, drops -F', file=sys.stderr)
