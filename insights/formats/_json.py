import json
import sys

from insights.core import dr
from insights.core.evaluators import SingleEvaluator as Evaluator, get_simple_module_name
from insights.formats import EvaluatorFormatterAdapter, get_response_of_types, render


class JsonFormat(Evaluator):
    def __init__(self, broker=None, missing=False, render_content=False, show_rules=None, stream=sys.stdout):
        super(JsonFormat, self).__init__(broker, stream=stream)
        self.missing = missing
        self.render_content = render_content
        self.show_rules = [] if show_rules is None else show_rules

    def handle_result(self, plugin, r):
        type_ = r["type"]

        if type_ == "skip":
            self.rule_skips.append(r)
        elif type_ == "metadata":
            self.append_metadata(r)
        elif type_ == "metadata_key":
            self.metadata_keys[r.get_key()] = r["value"]
        else:
            comp = dr.get_name(plugin)
            key = r.get_key()
            response_id = "%s_id" % r.response_type
            result = {
                response_id: "{0}|{1}".format(get_simple_module_name(plugin), key),
                "component": comp,
                "type": type_,
                "key": key,
                "details": r,
                "tags": list(dr.get_tags(plugin)),
                "links": dr.get_delegate(plugin).links or {}
            }
            if self.render_content:
                result.update({"rendered_content": render(comp, r)})

            self.results[type_].append(self.format_result(result))

    def postprocess(self):
        response = get_response_of_types(self.get_response(), self.missing, self.show_rules)
        json.dump(response, self.stream)


class JsonFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = JsonFormat
