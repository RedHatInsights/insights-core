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
import datetime
import logging
from jinja2 import Environment
from operator import itemgetter

from insights.core import dr, filters
from insights.core import spec_factory as sf
from insights.core.plugins import is_rule
from insights.specs.default import DefaultSpecs
from insights.specs import Specs


logging.basicConfig(level=logging.INFO)


REPORT = """
<html><head><title>Spec to Rule Mapping Report ({{ report_date }})</title>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
</head>
<body>
<h2>Spec to Rule Mapping Report {{ report_date }}</h2>
<p>This is the mapping of Red Hat Insights Specs to Insights Rules they affect.</p>

<table class="table table-striped table-bordered">
<thead>
<tr><th>Spec Name</th><th>Spec</th><th>Rules</th><th>Filters</th></tr>
</thead>
<tbody>
{% for info in infos %}
    <tr>
        <td>{{ info.name }}</td>
        <td><code>{{ info.description }}</code></td>
        <td>{{ info.rules }}</td>
        <td>{{ info.filters }}</td>
    </tr>
{% endfor %}
</tbody>
</table>
</body></html>
""".strip()


def get_all(root, method=dr.get_dependencies):
    for d in method(root):
        yield d
        for c in get_all(d, method=method):
            yield c


def load_plugins():
    """ Load the plugins we care about """
    dr.load_components("insights.specs.default")
    dr.load_components("insights.parsers")
    dr.load_components("insights.combiners")
    dr.load_components("telemetry.rules.plugins")
    dr.load_components("prodsec")


def get_specs():
    """
    Get default datasources that implement a `RegistryPoint` defined in
    `insights.specs.Specs`
    """
    vals = vars(Specs).values()
    sd = sf.SpecDescriptor
    names = [d.__get__(d, None).__name__ for d in vals if isinstance(d, sd)]
    return [d for d in [getattr(DefaultSpecs, name, None) for name in names] if d]


def li(item):
    return "<li>%s</li>" % item


def ul(lst):
    return "<ul>\n%s\n</ul>\n" % "\n".join(li(i) for i in lst)


def get_description(spec):
    if isinstance(spec, sf.simple_file):
        return "Path: %s" % spec.path
    if isinstance(spec, sf.glob_file):
        return "All files matching any of%sIgnore: %s" % (ul(spec.patterns), spec.ignore)
    if isinstance(spec, sf.simple_command):
        return "Command: %s" % spec.cmd
    if isinstance(spec, sf.listdir):
        return "Directory Listing: %s" % spec.path
    if isinstance(spec, sf.foreach_execute):
        return "For each element in%s Command: %s" % (ul([get_description(spec.provider)]), spec.cmd)
    if isinstance(spec, sf.foreach_collect):
        return "For each element in%s Path: %s" % (ul([get_description(spec.provider)]), spec.path)
    if isinstance(spec, sf.first_of):
        return "First of%s" % ul(get_description(d) for d in spec.deps)
    if isinstance(spec, sf.first_file):
        return "First file of%s" % ul(spec.files)
    return (spec.__doc__ or "").replace("\n", "<br />")


def get_rules(spec):
    return [r for r in get_all(spec, method=dr.get_dependents) if is_rule(r)]


def get_infos(specs):
    def get_info(spec):
        return {
            "name": dr.get_simple_name(spec),
            "description": get_description(spec),
            "rules": ul(sorted(dr.get_name(r) for r in get_rules(spec))),
            "filters": ul(sorted(filters.get_filters(spec))),
        }
    return sorted((get_info(s) for s in specs), key=itemgetter("name"))


def main():
    today = datetime.date.today().strftime("%B %d, %Y")
    load_plugins()
    specs = get_specs()
    infos = get_infos(specs)

    template = Environment().from_string(REPORT)
    report = template.render(report_date=today, infos=infos)
    print(report)


if __name__ == "__main__":
    main()
