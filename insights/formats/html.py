from __future__ import print_function
from collections import OrderedDict
from itertools import groupby
from operator import itemgetter

from insights import make_info, make_fail, make_response, make_pass
from insights.formats import FormatterAdapter
from insights.formats.template import TemplateFormat


class HtmlFormat(TemplateFormat):
    """
    This class prints a html summary of rule hits. It should be used
    as a context manager and given an instance of an
    ``insights.core.dr.Broker``. ``dr.run`` should be called within the context
    using the same broker.

    Args:
        broker (Broker): the broker to watch and provide a summary about.
        stream (file-like): Output is written to stream. Defaults to sys.stdout.
    """

    TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

    <title>{{root}}</title>
  </head>
  <body>
    <div class="container">
      <p>
        <h2>Analysis of {{root}}</h2>
        <h4>Performed at {{start_time}} UTC</h4>
      </p>
      <div class="card">
        <div class="card-header">System Information</div>
        <div class="card-body">
        <pre>
{% for rule in rules.make_info %}
{{-rule.body}}
{% endfor -%}
        </pre>
        </div>
      </div>
      <div class="card">
        <div class="card-header">Rule Results</div>
        <div class="card-body">
          <div class="accordion" id="ruleAccordion">
          {%- for group, results in rules.items() %}
          {%- if group != "make_info" %}
          {%- for rule in results %}
            <div class="card">
              <div class="card-header bg-{% if group == "make_pass" %}success{% else %}danger{% endif %}" id="heading_{{rule.id}}">
                <h2 class="mb-0">
                  <button class="btn btn-{% if group == "make_pass" %}success{% else %}danger{% endif %} text-white" type="button" data-toggle="collapse" data-target="#{{rule.id}}" aria-expanded="true" aria-controls="{{rule.id}}">
                  {{rule.name}}
                  </button>
                </h2>
              </div>
              <div id="{{rule.id}}" class="collapse" aria-labelledby="heading_{{rule.id}}" data-parent="#ruleAccordion">
                <div class="card-body">
                <pre>
{{rule.body}}
                </pre>
                <hr />
                Contributing data:
                <ol>
                {% for d in rule.datasources %}
                  <li>
                  {{d}}
                  </li>
                {%- endfor %}
                </ol>
                <hr />
                Links:
                <ul>
                {% for cat, links in rule.links.items() %}
                  <li>{{cat}}
                  <ul>
                  {% for link in links %}
                  <li><a href="{{link}}">{{link}}</a></li>
                  {% endfor %}
                  </ul>
                  </li>
                {%- endfor %}
                </ul>
                <hr />
                Rule source: {{rule.source_path}}
                <hr />
          Documentation:
                <pre>
{{rule.mod_doc}}
{{rule.rule_doc}}
                </pre>
                </div>
              </div>
            </div>
          {%- endfor %}
          {% endif %}
          {% endfor %}
          </div>
        </div>
      </div>
    </div>
    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script
        src="http://code.jquery.com/jquery-3.4.1.slim.min.js"
        integrity="sha256-pasqAKBDmFT4eHoN2ndd6lN370kFiGUFyTiUHWhU7k8="
        crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
  </body>
</html>
    """.strip()

    def create_template_context(self):
        ctx = {
            "root": self.find_root() or "Unknown",
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        sorted_rules = {}
        response_type_getter = itemgetter("response_type")

        self.rules = sorted(self.rules, key=response_type_getter)
        for response_type, rules in groupby(self.rules, response_type_getter):
            rules = sorted(rules, key=itemgetter("name"))
            sorted_rules[response_type] = rules

        ctx["rules"] = OrderedDict()
        for key in (make_info, make_fail, make_response, make_pass):
            name = key.__name__
            if name in sorted_rules:
                ctx["rules"][name] = sorted_rules[name]
        return ctx


# this connects the formatter to the insights run CLI bits
class HtmlFormatterAdapter(FormatterAdapter):
    """ Displays results in html format. """

    def preprocess(self, broker):
        self.formatter = HtmlFormat(broker)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()
