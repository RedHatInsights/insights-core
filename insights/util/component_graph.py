#!/usr/bin/env python
"""
This module loads all of the components: specs, parsers and combiners, and
creates an `.rst` file output which can be included in the documentation
build.  The output file is a cross-reference for each type of component,
showing the component's dependents and dependencies.  In the case of
specs it only shows the dependents, and does not currently use the
context specific specs.

It can be called from the commandline to manually generate the file or
it may also be called inside the Sphinx *conf.py* `setup` function to
generate the documentation automatically.

Command Line Use
----------------

This assumes that you have a working installation of insights-core
and python environment for insights-core development.

To run from the command line simply execute this utility and provide
the name of the output file::

    $ python insights/util/component_graph.py output_filename.rst

"""

import argparse
from insights.core import dr
from insights.core.plugins import is_datasource, is_parser, is_combiner


def blank_line(fh, number=1):
    for l in range(number):
        fh.write("\n")


def print_info(info, fh):
    fh.write("* :py:obj:`{}`\n".format(info['name']))
    blank_line(fh)

    if info['dependents']:
        fh.write("  * Dependents:\n")
        blank_line(fh)
        for d in info['dependents']:
            fh.write("    * :py:obj:`{}`\n".format(d))
    else:
        fh.write("  * Dependents: None\n")
    blank_line(fh)

    if info['dependencies']:
        fh.write("  * Dependencies:\n")
        blank_line(fh)
        for d in info['dependencies']:
            fh.write("    * :py:obj:`{}`\n".format(d))
    else:
        fh.write("  * Dependencies: None\n")
    blank_line(fh)


def print_spec_info(info, fh):
    fh.write("* :py:obj:`{}`\n".format(info['name']))
    blank_line(fh)

    if info['dependents']:
        fh.write("  * Dependents:\n")
        blank_line(fh)
        for d in info['dependents']:
            fh.write("    * :py:obj:`{}`\n".format(d['name']))
            blank_line(fh)
            if d['dependents']:
                fh.write("      * Sub-Dependents:\n")
                blank_line(fh)
                for sd in d['dependents']:
                    fh.write("        * :py:obj:`{}`\n".format(sd))
            else:
                fh.write("      * Sub-Dependents: None\n")
            blank_line(fh)
    else:
        fh.write("  * Dependents: None\n")
    blank_line(fh)


def component_info(component):
    dependents = dr.get_dependents(component)
    dependencies = dr.get_dependencies(component)
    return {
        'name': dr.get_name(component),
        'dependents': [
            dr.get_name(c)
            for c in dependents
        ],
        'dependencies': [
            dr.get_name(c)
            for c in dependencies
        ]
    }


def main(filename):
    dr.load_components("insights.specs.default")
    dr.load_components("insights.specs.insights_archive")
    dr.load_components("insights.specs.sos_archive")
    dr.load_components("insights.specs.jdr_archive")
    dr.load_components("insights.parsers")
    dr.load_components("insights.combiners")

    parsers = sorted([c for c in dr.DELEGATES if is_parser(c)], key=dr.get_name)
    combiners = sorted([c for c in dr.DELEGATES if is_combiner(c)], key=dr.get_name)
    specs = sorted([c for c in dr.DELEGATES
                    if is_datasource(c) and dr.get_module_name(c) == 'insights.specs'],
                   key=dr.get_name)

    with open(filename, "w") as fh:
        fh.write("Components Cross-Reference\n")
        fh.write("==========================\n")

        fh.write("Specs Dependents\n")
        fh.write("----------------\n")
        for spec in specs:
            info = dict(name=dr.get_name(spec))
            info['dependents'] = []
            for d in dr.get_dependents(spec):
                info['dependents'].append({
                    'name': dr.get_name(d),
                    'dependents': [dr.get_name(sd) for sd in dr.get_dependents(d)]
                })
            print_spec_info(info, fh)

        blank_line(fh)
        fh.write("Parser Dependents/Dependencies\n")
        fh.write("------------------------------\n")
        for pars in parsers:
            print_info(component_info(pars), fh)

        blank_line(fh)
        fh.write("Combiner Dependents/Dependencies\n")
        fh.write("--------------------------------\n")
        for comb in combiners:
            print_info(component_info(comb), fh)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("out_filename", help="Name of the output file to write the cross-reference")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.out_filename)
