#!/usr/bin/env python
"""
The inspect module allows you to execute an insights component
(parser, combiner, rule or datasource) dropping you into an
ipython session where you can inspect the outcome.


>>> insights-inspect insights.parsers.hostname.Hostname
IPython Console Usage Info:
Enter 'make_pass.' and tab to get a list of properties
Example:
In [1]: make_pass.<property_name>
Out[1]: <property value>
To exit ipython enter 'exit' and hit enter or use 'CTL D'
Python 3.6.6 (default, Jul 19 2018, 14:25:17)
Type "copyright", "credits" or "license" for more information.
IPython 5.8.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
In [1]: Hostname.fqdn
Out[1]: 'lhuett.usersys.redhat.com'"


>>> insights-inspect insights.combiners.hostname.hostname
IPython Console Usage Info:
Enter 'make_pass.' and tab to get a list of properties
Example:
In [1]: make_pass.<property_name>
Out[1]: <property value>
To exit ipython enter 'exit' and hit enter or use 'CTL D'
Python 3.6.6 (default, Jul 19 2018, 14:25:17)
Type "copyright", "credits" or "license" for more information.
IPython 5.8.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
In [1]: Hostname.fqdn
Out[1]: 'lhuett.usersys.redhat.com'


>>> insights-inspect insights.specs.Specs.hostname
IPython Console Usage Info:
Enter 'make_pass.' and tab to get a list of properties
Example:
In [1]: make_pass.<property_name>
Out[1]: <property value>
To exit ipython enter 'exit' and hit enter or use 'CTL D'
Python 3.6.6 (default, Jul 19 2018, 14:25:17)
Type "copyright", "credits" or "license" for more information.
IPython 5.8.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
In [1]: CommandOutputProvider.cmd
Out[1]: '/usr/bin/hostname -f'


>>> insights-inspect examples.rules.bash_version.report
IPython Console Usage Info:
Enter 'make_pass.' and tab to get a list of properties
Example:
In [1]: make_pass.<property_name>
Out[1]: <property value>
To exit ipython enter 'exit' and hit enter or use 'CTL D'
Python 3.6.6 (default, Jul 19 2018, 14:25:17)
Type "copyright", "credits" or "license" for more information.
IPython 5.8.0 -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
In [1]: make_pass.values()
Out[1]: dict_values([0:bash-4.2.46-31.el7, 'pass', 'BASH_VERSION'])
In [2]: broker.keys()
Out[2]: dict_keys([<class 'insights.core.context.HostArchiveContext'>,
<insights.core.spec_factory.glob_file object at 0x7f0303c93390>,
<insights.core.spec_factory.head object at 0x7f0303cabef0>,
insights.specs.Specs.installed_rpms,
<class 'insights.parsers.installed_rpms.InstalledRpms'>,
<function report at 0x7f0303c679d8>])
In [3]: p = broker[insights.parsers.installed_rpms.InstalledRpms]
In [4]: a = p.get_max('bash')
In [5]: a.nevra
Out[5]: 'bash-0:4.2.46-31.el7.x86_64'
"""

from __future__ import print_function
import argparse
import logging
import os
import sys
import yaml
from IPython import embed

from contextlib import contextmanager

from insights import (apply_configs, create_context, dr, extract, HostContext,
                      load_default_plugins)

try:
    import colorama as C
    C.init()
except:
    class Pass(object):
        def _getattr__(self, name):
            return ""

    class C(object):
        Fore = Pass()
        Style = Pass()


def parse_args():
    p = argparse.ArgumentParser("Insights component runner.")
    p.add_argument("-c", "--config", help="Configure components.")
    p.add_argument("-D", "--debug", action="store_true", help="Show debug level information.")
    p.add_argument("component", nargs=1, help="Component to inspect.")
    p.add_argument("archive", nargs="?", help="Archive or directory to analyze.")
    return p.parse_args()


def configure_logging(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)


def configure(config):
    if config:
        with open(config) as f:
            apply_configs(yaml.safe_load(f))


def get_component(fqdn):
    return dr.get_component(fqdn)


@contextmanager
def create_broker(root=None):
    if not root:
        broker = dr.Broker()
        broker[HostContext] = HostContext()
        yield broker
    else:
        def from_dir(d):
            broker = dr.Broker()
            ctx = create_context(d, None)
            broker[ctx.__class__] = ctx
            return broker

        if os.path.isdir(root):
            yield from_dir(root)
        else:
            with extract(root) as ex:
                yield from_dir(ex.tmp_dir)


def dump_error(component, broker):
    if component in broker.exceptions:
        for ex in broker.exceptions[component]:
            print(broker.tracebacks[ex], file=sys.stderr)

    if component in broker.missing_requirements:
        missing = broker.missing_requirements[component]
        required = missing[0]
        at_least_one = missing[1]

        buf = sys.stderr

        print("Missing Dependencies:", file=buf)
        if required:
            print("    Requires:", file=buf)
            for d in required:
                print("        %s" % dr.get_name(d), file=buf)
        if at_least_one:
            for alo in at_least_one:
                print("    At Least One Of:", file=buf)
                for d in alo:
                    print("        %s" % dr.get_name(d), file=buf)


def run(component, archive=None):
    with create_broker(archive) as broker:
        value = dr.run(component, broker=broker).get(component)
        name = dr.get_name(component).rsplit(".", 1)[1]
        vars()[name] = value
        if value:
            print(C.Fore.BLUE + "\nIPython Console Usage Info:\n" + C.Style.RESET_ALL, file=sys.stderr)
            print("Enter '{}.' and tab to get a list of properties ".format(name))
            print("Example:")
            print("In [1]: {}.<property_name>".format(name))
            print("Out[1]: <property value>\n")
            print("To exit ipython enter 'exit' and hit enter or use 'CTL D'\n\n")
            embed()
        else:
            dump_error(component, broker)
            return sys.exit(1)


def main():
    args = parse_args()
    configure_logging(args.debug)
    configure(args.config)
    load_default_plugins()
    component = get_component(args.component[0])
    if not component:
        print("Component not found: %s" % args.component[0], file=sys.stderr)
        sys.exit(1)
    run(component, archive=args.archive)


if __name__ == "__main__":
    main()
