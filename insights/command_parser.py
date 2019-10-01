#!/usr/bin/env python
"""
Command Parser module
---------------------
Implements the ``insights`` command line.  Each function is the first
argument followed by the function specific arguments.  See USAGE text
below.
"""
from __future__ import print_function

import argparse
import sys

USAGE = """insights <command> [<args>]
Available commands:
  cat         Execute a spec and show the output
  collect     Collect all specs against the client and create an Insights archive.
  inspect     Execute component and shell out to ipython for evaluation.
  info        View info and docs for Insights Core components.
  ocpshell         Interactive evaluation of archives, directories, or individual yaml files.
  run         Run insights-core against host or an archive.
"""


class InsightsCli(object):
    """
    Class to implement the cli module.
    Each command is called as a method of this class and all
    arg parsing is performed in the separate module that
    actually implements the command.  the args "insights command"
    are not passed to the submodule.
    """

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Insights Core command line execution",
            usage=USAGE)
        parser.add_argument('command', help='Insights Core command to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            sys.exit(1)
        # remove the sub-command arg from sys.argv
        sys.argv.pop(1)
        # Use dispatch pattern to execute command
        getattr(self, args.command)()

    def cat(self):
        from .tools.cat import main as cat_main
        cat_main()

    def collect(self):
        from .collect import main as collect_main
        collect_main()

    def info(self):
        from .tools.query import main as query_main
        query_main()

    def inspect(self):
        from .tools.insights_inspect import main as inspect_main
        inspect_main()

    def ocpshell(self):
        from .ocpshell import main as ocpshell_main
        ocpshell_main()

    def run(self):
        from insights import run
        if "" not in sys.path:
            sys.path.insert(0, "")
        run(print_summary=True)


def fix_arg_dashes():

    en_dash = '\u2013'
    em_dash = '\u2014'

    # replace unicode (en dash and em dash) dashes from argument definitions that may have been copy
    # and pasted from another source
    i = 1
    for a in sys.argv[1:]:
        first = list(a)
        first[0] = first[0].replace(em_dash, "--").replace(en_dash, "-")
        sys.argv[i] = "".join(first)
        i += 1


def main():
    fix_arg_dashes()
    try:
        InsightsCli()
    except SystemExit:
        raise
    except BaseException as ex:
        print(ex)


if __name__ == "__main__":
    main()
