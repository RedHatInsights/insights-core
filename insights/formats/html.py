from __future__ import print_function
import inspect
import sys
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime

from jinja2 import Template

from insights import dr, rule, make_info, make_fail, make_pass, make_response
from insights.core.context import ExecutionContext
from insights.core.spec_factory import ContentProvider
from insights.core.plugins import is_datasource
from insights.formats import render, Formatter, FormatterAdapter


class HtmlFormatter(Formatter):
    CONTENT = """
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
{% endfor %}
            </pre
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
                    {% endfor %}
                    </ol>
                    <hr />
              Documentation:
                    <pre>
{{rule.mod_doc}}
{{rule.rule_doc}}
                    </pre>
                    <hr />
                    Rule source: {{rule.rule_path}}
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
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
      </body>
    </html>
    """

    def find_root(self):
        """
        Finds the root directory used during the evaluation. Note this could be
        a non-existent temporary directory if analyzing an archive.
        """
        for comp in self.broker:
            if issubclass(comp, ExecutionContext):
                return self.broker[comp].root

    def collect(self, comp, broker):
        """
        Store rule results organized by response type.
        """
        if comp in broker:
            val = broker[comp]
            self.groups[type(val)].append((comp, val))

    def get_datasources(self, comp, broker):
        """
        Get the most relevant activated datasources for each rule.
        """
        graph = dr.get_dependency_graph(comp)
        for cand in graph:
            if cand in broker and is_datasource(cand):
                val = broker[cand]
                if not isinstance(val, list):
                    val = [val]

                results = []
                for v in val:
                    if isinstance(v, ContentProvider):
                        results.append(v.cmd or v.path or "python implementation")

                self.datasources[comp].extend(results)

    def preprocess(self):
        """
        Watches rules go by as they evaluate and collects information about
        them for later display in postprocess.
        """
        self.start_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.groups = defaultdict(list)
        self.datasources = defaultdict(list)
        self.broker.add_observer(self.collect, rule)
        self.broker.add_observer(self.get_datasources, rule)

    def postprocess(self):
        """
        Builds a dictionary of rule data as context for a jinja2 template that
        renders the final output.
        """
        root = self.find_root() or "Unknown"

        ctx = {
            "root": root,
            "start_time": self.start_time,
            "rules": OrderedDict(),
        }
        types = (make_info, make_fail, make_response, make_pass)
        for key in types:
            group = self.groups[key]
            response_type = key.__name__
            ctx["rules"][response_type] = []
            for comp, val in sorted(group, key=lambda g: dr.get_name(g[0])):
                if isinstance(val, types):
                    name = dr.get_name(comp)
                    rule_id = name.replace(".", "_")
                    ctx["rules"][response_type].append({
                        "id": rule_id,
                        "name": name,
                        "body": render(comp, val),
                        "mod_doc": sys.modules[comp.__module__].__doc__ or "",
                        "rule_doc": comp.__doc__ or "",
                        "rule_path": inspect.getabsfile(comp),
                        "datasources": sorted(set(self.datasources[comp]))
                    })
        print(Template(self.CONTENT).render(ctx), file=self.stream)


# this connects the formatter to the insights run CLI bits
class HtmlFormatterAdapter(FormatterAdapter):
    def preprocess(self, broker):
        self.formatter = HtmlFormatter(broker)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()
