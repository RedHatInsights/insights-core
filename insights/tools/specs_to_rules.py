#!/usr/bin/env python
"""
Create a mapping of specs, rules and filters for each parser

To run this script execute the following commands:
$ cd insights-core
$ source bin/activate
$ cd ../insights-plugins
$ export PYTHONPATH=./
$ ../insights-core/insights/tools/specs_to_rules.py > report.html

"""
from collections import defaultdict
import datetime
from insights.core import dr, filters
from jinja2 import Environment
from insights.core.plugins import is_datasource

REPORT = """
<html><head><title>Parser Rule Mapping Report ({{ report_date }})</title>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
</head>
<body>
<h2>Parser Rule Mapping Report {{ report_date }}</h2>
<p>This is the mapping of Red Hat Insights Parsers to Insights Rules that utilize those parsers.</p>

<table class="table table-striped table-bordered">
<thead>
<tr><th>Spec Name</th><th>Spec</th><th>Rules</th><th>Filters</th></tr>
</thead>
<tbody>
{% for name in specs.keys()|sort %}
    {% for spec in specs[name].keys() %}
        {% if "_filters" not in spec %}
            <tr>
                <td>{{ name }}</td>
                <td><code>{{ spec.strip('<>') }}</code></td>
                <td>{{ specs[name][spec] }}</td>
                <td>
                    {% for f in specs[name][name + "_filters"] %}
                       <li>{{ f|e }}</li>
                    {% endfor %}
                </td>
            </tr>
        {% endif %}
    {% endfor %}
{% endfor %}
</tbody>
</table>
</body></html>
""".strip()


def main():
    # config = get_config()

    dr.load_components("insights.specs.default")
    dr.load_components("insights.specs.insights_archive")
    dr.load_components("insights.specs.sos_archive")
    dr.load_components("insights.parsers")
    dr.load_components("insights.combiners")
    dr.load_components("telemetry.rules.plugins")
    dr.load_components("prodsec")

    # parsers = sorted([c for c in dr.DELEGATES if is_parser(c)], key=dr.get_simple_name)
    # combiners = sorted([c for c in dr.DELEGATES if is_combiner(c)], key=dr.get_name)
    specs = sorted([c for c in dr.DELEGATES
                    if is_datasource(c) and dr.get_module_name(c) == 'insights.specs'],
                   key=dr.get_simple_name)

    deps = defaultdict(dict)

    for spec in specs:
        info = dict(name=dr.get_simple_name(spec))
        f = filters.get_filters(spec)
        info['dependents'] = []
        for d in dr.get_dependents(spec):
            p = [dr.get_name(sd) for sd in dr.get_dependents(d)]
            rules = sorted([x.rsplit('.', 2)[1] for x in p])
            deps[info['name']][info['name']] = ", ".join(rules)
            deps[info['name']][info['name'] + "_filters"] = f

    report = Environment().from_string(REPORT).render(
        report_date=datetime.date.today().strftime("%B %d, %Y"), specs=deps)

    print(report)


if __name__ == "__main__":
    main()
