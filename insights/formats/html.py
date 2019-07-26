from __future__ import print_function
import inspect
import sys
from collections import defaultdict
from datetime import datetime

from jinja2 import Template

from insights import dr, rule, make_info, make_fail, make_pass, make_response
from insights.core.plugins import is_datasource
from insights.core.context import ExecutionContext
from insights.formats import render, Formatter, FormatterAdapter

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
        {% for info in infos %}
{{-info}}
        {% endfor %}
        </pre
        </div>
      </div>
      <div class="card">
        <div class="card-header">Rule Results</div>
        <div class="card-body">
          <div class="accordion" id="ruleAccordion">
          {% for group, results in rules.items() %}
          {% for rule in results %}
            <div class="card">
              <div class="card-header bg-{{rule.color}}" id="heading_{{rule.id}}">
                <h2 class="mb-0">
                  <button class="btn btn-{{rule.color}} text-white" type="button" data-toggle="collapse" data-target="#{{rule.id}}" aria-expanded="true" aria-controls="{{rule.id}}">
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
          Documentation:
                <pre>
{{rule.mod_doc}}
{{rule.rule_doc}}
                </pre>
                <hr />
                Rule source: {{rule.rule_path}}
                <hr />
                Contributing data:
                <ol>
                {% for d in rule.data %}
                  <li>
                  {{d}}
                  </li>
                {% endfor %}
                </ol>
                </div>
              </div>
            </div>
          {%- endfor %}
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

COLORS = {
    make_info: "info",
    make_fail: "danger",
    make_pass: "success",
}


class HtmlFormatter(Formatter):
    def find_root(self):
        for comp in self.broker:
            if issubclass(comp, ExecutionContext):
                return self.broker[comp].root

    def collect(self, comp, broker):
        if comp in broker:
            val = broker[comp]
            self.groups[type(val)].append((comp, val))

    def preprocess(self):
        self.start_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.groups = defaultdict(list)
        self.datasources = defaultdict(list)
        self.broker.add_observer(self.collect, rule)
        self.broker.add_observer(self.get_data_locations, rule)

    def get_data_locations(self, comp, broker):
        graph = dr.get_dependency_graph(comp)
        template = "{name}: {detail}"
        for cand in graph:
            if cand in broker and is_datasource(cand) and not any(is_datasource(d) for d in dr.get_dependencies(cand)):
                val = broker[cand]
                if not isinstance(val, list):
                    val = [val]

                results = []
                for v in val:
                    name = cand.__name__
                    detail = v.cmd or v.path or "python implementation"
                    results.append(template.format(name=name, detail=detail))

                self.datasources[comp].extend(results)

    def postprocess(self):
        root = self.find_root() or "Unknown"

        infos = self.groups[make_info]
        info_content = []
        for comp, val in sorted(infos, key=lambda g: dr.get_name(g[0])):
            info_content.append(render(comp, val))

        data = {
            "root": root,
            "start_time": self.start_time,
            "rules": {},
            "infos": info_content
        }
        for key in (make_fail, make_pass):
            group = self.groups[key]
            data["rules"][key.__name__] = []
            for comp, val in sorted(group, key=lambda g: dr.get_name(g[0])):
                if type(val) in (make_pass, make_fail, make_response):
                    rule_path = inspect.getabsfile(comp)
                    mod_doc = sys.modules[comp.__module__].__doc__ or ""
                    rule_doc = comp.__doc__ or ""
                    name = dr.get_name(comp)
                    rule_id = name.replace(".", "_")
                    data["rules"][key.__name__].append({
                        "color": COLORS[key],
                        "id": rule_id,
                        "name": name,
                        "body": render(comp, val),
                        "mod_doc": mod_doc,
                        "rule_doc": rule_doc,
                        "rule_path": rule_path,
                        "data": sorted(set(self.datasources[comp]))
                    })
        print(Template(CONTENT).render(data), file=self.stream)


# this connects the formatter to the insights run CLI bits
class HtmlFormatterAdapter(FormatterAdapter):
    def preprocess(self, broker):
        self.formatter = HtmlFormatter(broker)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()
