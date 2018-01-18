#!/usr/bin/env python

import argparse
import os
from insights.config import CommandSpec

mangle_command = CommandSpec.mangle_command


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("command", help="Command string to mangle.")
    return p.parse_args()


def main():
    args = parse_args()
    print os.path.join("insights_commands", mangle_command(args.command))


if __name__ == "__main__":
    main()
