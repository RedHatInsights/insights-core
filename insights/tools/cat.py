#!/usr/bin/env python
"""
The cat module allows you to execute an insights datasource and write its
output to stdout. A string representation of the datasource is written to
stderr before the output.

>>> insights-cat hostname
CommandOutputProvider("/usr/bin/hostname -f")
alonzo

Pass -q if you want only the datasource information.

>>> insights-cat -q ethtool
CommandOutputProvider("/sbin/ethtool docker0")
CommandOutputProvider("/sbin/ethtool enp0s31f6")
CommandOutputProvider("/sbin/ethtool lo")
CommandOutputProvider("/sbin/ethtool tun0")
CommandOutputProvider("/sbin/ethtool virbr0")
CommandOutputProvider("/sbin/ethtool virbr0-nic")
CommandOutputProvider("/sbin/ethtool wlp3s0")
"""
from __future__ import print_function
import argparse
import logging
import os
import sys
import yaml

from contextlib import contextmanager

from insights import (apply_configs, dr, extract, HostContext,
        load_default_plugins)
from insights.core.hydration import initialize_broker
from insights.core.spec_factory import ContentProvider

try:
    import colorama as C
    C.init()
except:
    class Pass(object):
        def __getattr__(self, name):
            return ""

    class C(object):
        Fore = Pass()
        Style = Pass()


def parse_args():
    p = argparse.ArgumentParser("Insights spec runner.")
    p.add_argument("-c", "--config", help="Configure components.")
    p.add_argument("-p", "--plugins", default="", help="Comma-separated list without spaces of package(s) or module(s) containing plugins.")
    p.add_argument("-q", "--quiet", action="store_true", help="Only show commands or paths.")
    p.add_argument("--no-header", action="store_true", help="Don't print command or path headers.")
    p.add_argument("-D", "--debug", action="store_true", help="Show debug level information.")
    p.add_argument("spec", nargs=1, help="Spec to dump.")
    p.add_argument("archive", nargs="?", help="Archive or directory to analyze.")
    return p.parse_args()


def configure_logging(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)


def parse_plugins(raw):
    for path in raw.split(","):
        path = path.strip()
        if path.endswith(".py"):
            path, _ = os.path.splitext(path)
        path = path.rstrip("/").replace("/", ".")
        yield path


def load_plugins(raw):
    if raw:
        for p in parse_plugins(raw):
            dr.load_components(p, continue_on_error=False)


def configure(config):
    if config:
        with open(config) as f:
            apply_configs(yaml.safe_load(f))


def get_spec(fqdn):
    if "." not in fqdn:
        fqdn = "insights.specs.Specs.%s" % fqdn
    return dr.get_component(fqdn)


@contextmanager
def create_broker(root=None):
    if not root:
        broker = dr.Broker()
        broker[HostContext] = HostContext()
        yield broker
    else:
        def from_dir(d):
            # ctx is returned here, but its already in the broker so not needed
            _, broker = initialize_broker(d)
            return broker

        if os.path.isdir(root):
            yield from_dir(root)
        else:
            with extract(root) as ex:
                yield from_dir(ex.tmp_dir)


def dump_spec(value, quiet=False, no_header=False):
    if not value:
        return

    value = value if isinstance(value, list) else [value]
    for v in value:
        if not no_header:
            vname = str(v) if isinstance(v, ContentProvider) else "Raw Data"
            print(C.Fore.BLUE + vname + C.Style.RESET_ALL, file=sys.stderr)
        if not quiet:
            if isinstance(v, ContentProvider):
                for d in v.stream():
                    print(d)
            else:
                print(v)


def dump_error(spec, broker):
    if spec in broker.exceptions:
        for ex in broker.exceptions[spec]:
            print(broker.tracebacks[ex], file=sys.stderr)

    if spec in broker.missing_requirements:
        missing = broker.missing_requirements[spec]
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


def run(spec, archive=None, quiet=False, no_header=False):
    with create_broker(archive) as broker:
        value = dr.run(spec, broker=broker).get(spec)
        if value:
            dump_spec(value, quiet=quiet, no_header=no_header)
        else:
            dump_error(spec, broker)
            return sys.exit(1)


def main():
    args = parse_args()
    configure_logging(args.debug)
    load_default_plugins()
    load_plugins(args.plugins)
    configure(args.config)
    spec = get_spec(args.spec[0])
    if not spec:
        print("Spec not found: %s" % args.spec[0], file=sys.stderr)
        sys.exit(1)
    run(spec, archive=args.archive, quiet=args.quiet, no_header=args.no_header)


if __name__ == "__main__":
    main()
