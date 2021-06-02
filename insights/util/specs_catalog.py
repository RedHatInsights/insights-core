#!/usr/bin/env python
"""
This module uses the inspec module to introspec information about
all of the datasources and dynamically create a ``.rst`` document to be
included in the sphinx build process

The output file is a listing of all default specs defined in
:py:mod:`insights.specs.default`.

It can be called from the commandline to manually generate the file or
it may also be called inside the Sphinx *conf.py* `setup` function to
generate the documentation automatically.

Command Line Use
----------------

This assumes that you have a working installation of insights-core
and python environment for insights-core development.

To run from the command line simply execute this utility and provide
the name of the output file::

    $ python -m insights.util.specs_catalog.main output_filename.rst

"""
import argparse
from insights.util.autology.datasources import DefaultSpecs

TEMPLATE = """
Datasource Catalog
==================

This catalog of specs provides the definitions for each of the specs the Insights Client
can collect. The format for this file is ``name = collection_type(collection_arguments)``.
A detailed description of the collection_types can be found in :ref:`datasources-ref`.
A summary of the collection_types includes:

* *simple_file* - collects the contents of a file
* *simple_command* - collects the output from a command
* *glob_file* - collects contents of all files matching the glob pattern
* *first_file* - collects the contents of the first file detected in a list
  of files
* *listdir* - collects the output of the ``ls`` command for the file/glob argument
* *foreach_execute* - collects the output of the command for each ``provider`` argument
* *foreach_collect* - collects the contents of the path created by replacing
  each element in the provider into the path
* *first_of* - collects the contents of datasource that returns data
* *command_with_args* - collects the output of the command with each ``provider`` argument
* *head* - collects the contents of the first item in a list

Some datasources are implemented as functions and each links to the details provided in the
function specific documentation.  Generally functions are used as a ``provider`` to other
datasources to, for instance, get a list of running processes of a particular program.
Functions implemented as custom datasources can be found in :ref:`custom-datasources`.

Python code that implements these datasources is located in the module
:py:mod:`insights.specs.default`.  The datasources each have a unique name in the
class :py:class:`insights.specs.default.DefaultSpecs`.

Datasources
-----------

Functions
^^^^^^^^^

.. hlist::
""".strip()


def blank_line(fh, number=1):
    for l in range(number):
        fh.write("\n")


def main(filename):
    defaultspecs = DefaultSpecs()
    with open(filename, "w") as fh:
        fh.write(TEMPLATE)
        blank_line(fh, 2)
        functions = [v for v in defaultspecs.values() if v.is_function]
        for v in functions:
            try:
                fh.write('    * :py:func:`{fxn_name}() <insights.specs.default.DefaultSpecs.{fxn_name}>`\n'.format(fxn_name=v['fxn_name']))
            except Exception:
                print('Error with function spec: {name}'.format(name=v['fxn_name']))

        fh.write('\n\nGeneral Datasources\n^^^^^^^^^^^^^^^^^^^\n\n::\n\n')

        for k, v in defaultspecs.items():
            try:
                if not v.is_function:
                    line = str(v)
                    line = line.replace('\n', '\\n')
                    fh.write('    {spec}\n'.format(spec=line))
            except Exception:
                print('Error with spec: {name}'.format(name=k))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("out_filename", help="Name of the output file to write the specs catalog")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.out_filename)
