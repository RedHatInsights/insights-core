#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import re


def mangle_command(command, name_max=255, has_variables=False):
    """
    Mangle a command line string into something suitable for use as the basename of a filename.
    At minimum this function must remove slashes, but it also does other things to clean up
    the basename: removing directory names from the command name, replacing many non-typical
    characters with undersores, in addition to replacing slashes with dots.

    By default, curly braces, '{' and '}', are replaced with underscore, set 'has_variables'
    to leave curly braces alone.

    This function was copied from the function that insights-client uses to create the name it uses
    to capture the output of the command.

    Here, server side, it is used to figure out what file in the archive contains the output of
    a command.  Server side, the command may contain references to variables (names within
    matching curly braces) that will be expanded before the name is actually used as a file name.

    To completly mimic the insights-client behavior, curly braces need to be replaced with
    underscores.  If the command has variable references, the curly braces must be left alone.
    Set has_variables, to leave curly braces alone.

    This implementation of 'has_variables' assumes that variable names only contain characters
    that are not replaced by mangle_command.
    """
    if has_variables:
        pattern = r"[^\w\-\.\/{}]+"
    else:
        pattern = r"[^\w\-\.\/]+"

    mangledname = re.sub(r"^/(usr/|)(bin|sbin)/", "", command)
    mangledname = re.sub(pattern, "_", mangledname)
    mangledname = re.sub(r"/", ".", mangledname).strip(" ._-")
    mangledname = mangledname[:name_max]
    return mangledname


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("command", help="Command string to mangle.")
    return p.parse_args()


def main():
    args = parse_args()
    print(os.path.join("insights_commands", mangle_command(args.command)))


if __name__ == "__main__":
    main()
