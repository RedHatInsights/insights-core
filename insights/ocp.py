#!/usr/bin/env python
import argparse
import logging
import os
import yaml
from insights.core.archives import extract
from insights.parsr.query import from_dict, Result
from insights.parsr.query import *  # noqa: F403

q = make_child_query  # noqa: F405

try:
    # go fast!
    # requires pyyaml installed with libyaml
    Loader = yaml.CLoader
    cloader = True
except:
    Loader = yaml.Loader
    cloader = False


log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("archives", nargs="+", help="Archive or directory to analyze.")
    return p.parse_args()


def get_ipshell():
    from IPython import embed
    from IPython.terminal.embed import InteractiveShellEmbed
    from IPython.core.completer import Completer

    Completer.use_jedi = False

    banner = """
    Openshift Configuration Explorer

    Tutorial: https://github.com/RedHatInsights/insights-core/blob/master/docs/notebooks/Parsr%20Query%20Tutorial.ipynb

    conf is the top level configuration. Use conf.get_keys() to see first level
    keys.

    Available Predicates
        lt, le, eq, gt, ge

        isin, contains

        startswith, endswith

        ieq, icontains, istartswith, iendswith

    Available Operators
        ~ (not)
        | (or)
        & (and)

    Example
        api = conf.where("kind", "KubeAPIServer")
        latest = api.status.latestAvailableRevision.value
        api.status.nodeStatuses.where("currentRevision", ~eq(latest))
    """
    exit_msg = '\nExiting IPython'

    try:
        return InteractiveShellEmbed(banner1=banner, exit_msg=exit_msg)
    except:
        return embed


def get_files(path):
    paths = []
    for root, dirs, names in os.walk(path):
        for name in names:
            p = os.path.join(root, name)
            if p.endswith(".yaml"):
                paths.append(p)
    return paths


def load(path):
    with open(path) as f:
        doc = yaml.load(f, Loader=Loader) if cloader else yaml.safe_load(f)
        return from_dict(doc)


def process(path):
    # cpu bound in yaml.load. threads don't help.
    return [load(p) for p in get_files(path)]


def analyze(paths):
    if not isinstance(paths, list):
        paths = [paths]

    results = []
    for path in paths:
        if os.path.isfile(path) and path.endswith((".yaml", ".yml")):
            results.append(load(path))
        elif os.path.isdir(path):
            results.extend(process(path))
        else:
            with extract(path) as ex:
                results.extend(process(ex.tmp_dir))

    return Result(children=results)


def main():
    args = parse_args()
    archives = args.archives
    conf = analyze(archives)  # noqa F841 / unused var

    shell = get_ipshell()
    shell()


if __name__ == "__main__":
    main()
