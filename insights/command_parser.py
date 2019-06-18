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

    def run(self):
        from insights import run
        if "" not in sys.path:
            sys.path.insert(0, "")
        run(print_summary=True)


def main():
    InsightsCli()


if __name__ == "__main__":
    main()
