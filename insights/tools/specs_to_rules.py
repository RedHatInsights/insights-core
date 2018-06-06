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
from insights.core.plugins import is_datasource, datasource


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
        {% if "_filters" not in spec %}
            <tr>
                <td>{{ name }}</td>
                <td><code>{{ specs[name][name + "_spec-def"] }}</code></td>
                <td>{{ specs[name][name + "_rules"] }}</td>
                <td>
                    {% for f in specs[name][name + "_filters"] %}
                       <li>{{ f|e }}</li>
                    {% endfor %}
                </td>
            </tr>
        {% endif %}
{% endfor %}
</tbody>
</table>
</body></html>
""".strip()


def main():
    # config = get_config()

    dr.load_components("insights.specs.default")
    dr.load_components("insights.parsers")
    dr.load_components("insights.combiners")
    dr.load_components("telemetry.rules.plugins")
    dr.load_components("prodsec")
    ds = dr.COMPONENTS_BY_TYPE[datasource]

    specs = []
    for c in ds:
        if not is_datasource(c):
            continue
        if not any(is_datasource(d) for d in dr.get_dependents(c)):
            specs.append(c)

    deps = defaultdict(dict)

    pspec = ''
    for spec in sorted(specs, key=dr.get_name):

        info = dict(name=dr.get_simple_name(spec))

        f = filters.get_filters(spec)
        info['dependents'] = []

        spds = None
        d = [d for d in dr.get_dependencies(spec) if is_datasource(d)]
        for dp in d:
            c = dr.get_dependencies(dp)
            for cdeps in c:
                if is_datasource(cdeps) and '__qualname__' in cdeps.func_dict and 'DefaultSpecs' in cdeps.func_dict['__qualname__']:
                    spds = cdeps

        for d in dr.get_dependencies(spec):
            cp = ''
            lines = []

            if d.__doc__ and "Returns the first" in d.__doc__:
                lines = d.__doc__.replace(',', '\n')
                lines = lines.splitlines()
                head = [lines[0]]
                top = ["<ul>"]
                bottom = ["</ul>"]
                if spds:
                    lines = [l.replace('Command:', '') for l in lines]
                    lines = [l.replace('Path:', '') for l in lines]
                    lines = ["<li>" + l + "</li>" for l in lines[1:]]
                    # lines = ["<li>" + spds.func_doc + ',' + l + "</li>" for l in lines[1:]]
                else:
                    lines = ["<li>" + l + "</li>" for l in lines[1:]]
                cp = "\n".join(head + top + lines + bottom)
            else:
                if spds:
                    d.__doc__ = d.__doc__.replace('Command:', '')
                    d.__doc__ = d.__doc__.replace('Path:', '')
                    d.__doc__ = spds.func_doc + ', ' + d.__doc__
                cp = d.__doc__

        for d in dr.get_dependents(spec):
            if dr.get_simple_name(pspec) == dr.get_simple_name(d):
                continue
            pspec = d

            p = [dr.get_name(sd) for sd in dr.get_dependents(d)]
            rules = sorted([x.rsplit('.', 2)[1] for x in p])
            deps[info['name']][info['name'] + "_spec-def"] = cp
            deps[info['name']][info['name'] + "_rules"] = ", ".join(rules)
            deps[info['name']][info['name'] + "_filters"] = f

    report = Environment().from_string(REPORT).render(
        report_date=datetime.date.today().strftime("%B %d, %Y"), specs=deps)

    print(report)


if __name__ == "__main__":
    main()
