#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import yaml

from insights.core import cluster, dr
from insights.core.archives import extract
from insights.core.hydration import create_context
from insights.formats.text import HumanReadableFormat
from insights.formats._yaml import YamlFormat
from insights.formats._json import JsonFormat


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("archive", nargs="?", help="Archive or directory to analyze")
    p.add_argument("-p", "--plugins", help="Comma separated package(s) or module(s) containing plugins to run.", default=None)
    p.add_argument("-t", "--topology", help="File containing extra data to pass to cluster rules")
    p.add_argument("-f", "--format", help="Output format [text|yaml|json]", default="insights.formats.text")
    p.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    return p.parse_args()


def process_archives(archives, args):
    for archive in sorted(archives):
        with extract(archive) as node:
            host = os.listdir(node.tmp_dir)[0]
            if args.verbose:
                print("Processing %s" % host)
            tmp_dir = os.path.join(node.tmp_dir, host)
            files = os.listdir(tmp_dir)
            tar_archive = [p for p in files if p.endswith(".tar")][0]
            sos_archive = [p for p in files if not (p.endswith(".tar") or p.endswith(".md5"))][0]
            with extract(os.path.join(tmp_dir, sos_archive)) as sos:
                ctx = create_context(sos.tmp_dir)
                with extract(os.path.join(tmp_dir, tar_archive), extract_dir=ctx.root):
                    broker = dr.Broker()
                    broker[ctx.__class__] = ctx
                    yield dr.run(broker=broker)


def process_cluster(uber_archive, broker, args, topology=None):
    topology = topology or {}
    with extract(uber_archive) as top:
        archives = os.listdir(top.tmp_dir)
        full_archives = [os.path.join(top.tmp_dir, a) for a in archives]
        brokers = process_archives(full_archives, args)
        facts = cluster.extract_facts(brokers)
        meta = cluster.ClusterMeta(len(archives), **topology)
        return cluster.process_facts(facts, meta, broker, use_pandas=True)


if __name__ == "__main__":
    args = parse_args()

    for plugin in ["default", "insights_archive", "sos_archive"]:
        dr.load_components("insights.specs.%s" % plugin)
    for plugin in args.plugins.split(","):
        dr.load_components(plugin)

    meta = {}
    if args.topology:
        with open(args.topology) as f:
            meta = yaml.load(f)

    broker = dr.Broker()
    if args.format.endswith("text"):
        with HumanReadableFormat(broker=broker):
            results_broker = process_cluster(args.archive, broker, args, meta)
    elif args.format.endswith("yaml"):
        with YamlFormat(broker=broker):
            results_broker = process_cluster(args.archive, broker, args, meta)
    elif args.format.endswith("json"):
        with JsonFormat(broker=broker):
            results_broker = process_cluster(args.archive, broker, args, meta)
    else:
        print("Invalid format specified: {}".format(args.format))

    print("Finished")
