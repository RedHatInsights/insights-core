#!/usr/bin/env python
"""
Create a mapping of specs and rules for each parser

To run this script execute the following commands:
$ cd insights-core
$ source bin/activate
$ cd ../insights-plugins
$ export PYTHONPATH=./
$ ../insights-core/insights/tools/specs_to_rules.py > report.html

"""
from collections import defaultdict
# import json
import datetime
from insights.core import plugins
from insights.config.factory import get_config
from jinja2 import Environment

REPORT = """
<html><head><title>Parser Rule Mapping Report ({{ report_date }})</title>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
</head>
<body>
<h2>Parser Rule Mapping Report {{ report_date }}</h2>
<p>This is the mapping of Red Hat Insights Parsers to Insights Rules that utilize those parsers.</p>

<table class="table table-striped table-bordered">
<thead>
<tr><th>Spec Name</th><th>Spec</th><th>Rules</th></tr>
</thead>
<tbody>
{% for name in specs.keys()|sort %}
    {% for spec in specs[name].keys() %}
<tr><td>{{ name }}</td><td><code>{{ spec.strip('<>') }}</code></td><td>{{ specs[name][spec] }}</td></tr>
    {% endfor %}
{% endfor %}
</tbody>
</table>
</body></html>
""".strip()


def main():
    config = get_config()

    plugins.load("insights.parsers")
    plugins.load("insights.combiners")
    plugins.load("telemetry.rules")

    parsers = [p for p in plugins.COMPONENTS_BY_TYPE[plugins.parser] if p.consumers]
    deps = defaultdict(dict)

    for p in parsers:
        for name in p.symbolic_names:
            spec = config.get_specs(name)
            rules = sorted(plugins.get_name(c) for c in p.consumers)
            for s in spec:
                deps[name][str(s)] = ", ".join(rules)

    # print json.dumps(dict(deps))

    report = Environment().from_string(REPORT).render(
        report_date=datetime.date.today().strftime("%B %d, %Y"), specs=deps)

    print(report)


if __name__ == "__main__":
    main()
