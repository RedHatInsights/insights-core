#!/usr/bin/env python
"""
This module runs insights and serializes the results into a directory. It is
configurable with a yaml manifest that specifies what to load, what to run,
and what to serialize. If a manifest isn't provided, a default one is used that
runs all datasources in ``insights.specs.Specs`` and
``insights.specs.default.DefaultSpecs`` and saves all datasources in
``insights.specs.Specs``.
"""
from __future__ import print_function

import argparse
import logging
import os
import sys
import tempfile
import yaml

from datetime import datetime

from insights import apply_configs, apply_default_enabled, get_pool
from insights.cleaner import Cleaner
from insights.core import blacklist, dr, filters
from insights.core.serde import Hydration
from insights.core.spec_factory import SAFE_ENV
from insights.specs.manifests import manifests
from insights.util import fs, utc
from insights.util.hostname import determine_hostname
from insights.util.subproc import call

log = logging.getLogger(__name__)

EXCEPTIONS_TO_REPORT = set([OSError])
"""Exception types that should be reported on after core collection."""


def load_manifest(data):
    """Helper for loading a manifest yaml doc."""
    if isinstance(data, dict):
        return data
    if os.path.isfile(data):
        with open(data, 'r') as f:
            doc = yaml.safe_load(f)
    else:
        doc = yaml.safe_load(data)
    if not isinstance(doc, dict):
        raise Exception("Manifest didn't result in dict.")
    return doc


def load_packages(pkgs):
    for p in pkgs:
        dr.load_components(p, continue_on_error=False)


def apply_blacklist(cfg):

    def _skip_component(component):
        dr.set_enabled(component, enabled=False)
        blacklist.BLACKLISTED_SPECS.append(component.split('.')[-1])
        log.warning('WARNING: Skipping component: %s' % component)

    def _check_and_skip_component(name):
        def _isidentifier(name):
            if hasattr(str, 'isidentifier'):
                return name.isidentifier()
            else:
                return not any(it in name for it in ('/', ' ', '.', '-'))

        if not _isidentifier(name):
            # not symbolic name
            return False
        # like a symbolic name
        component = 'insights.specs.default.DefaultSpecs.{0}'.format(name)
        if dr.get_component_by_name(component):
            # is a sybmolic name
            _skip_component(component)
            return True
        # not symbolic name
        return False

    for fil in cfg.get("files", []):
        if not _check_and_skip_component(fil):
            blacklist.add_file(fil)

    for cmd in cfg.get("commands", []):
        if not _check_and_skip_component(cmd):
            blacklist.add_command(cmd)

    for component in cfg.get('components', []):
        if not dr.get_component_by_name(component):
            log.warning('WARNING: Unknown component in blacklist: %s' % component)
        else:
            _skip_component(component)

    if cfg.get('patterns'):
        log.warning("WARNING: Excluding patterns defined in blacklist configuration")

    if cfg.get('keywords'):
        log.warning("WARNING: Replacing keywords defined in blacklist configuration")


def create_context(ctx):
    """
    Loads and constructs the specified context with the specified arguments.
    If a '.' isn't in the class name, the 'insights.core.context' package is
    assumed.
    """
    ctx_cls_name = ctx.get("class", "insights.core.context.HostContext")
    if "." not in ctx_cls_name:
        ctx_cls_name = "insights.core.context." + ctx_cls_name
    ctx_cls = dr.get_component(ctx_cls_name)
    ctx_args = ctx.get("args", {})
    return ctx_cls(**ctx_args)


def get_to_persist(persisters):
    """
    Given a specification of what to persist, generates the corresponding set
    of components.
    """

    def specs():
        for p in persisters:
            if isinstance(p, dict):
                yield p["name"], p.get("enabled", True)
            else:
                yield p, True

    components = sorted(dr.DELEGATES, key=dr.get_name)
    names = dict((c, dr.get_name(c)) for c in components)

    results = set()
    for p, e in specs():
        for c in components:
            if names[c].startswith(p):
                if e:
                    results.add(c)
                elif c in results:
                    results.remove(c)
    return results


def create_archive(path, remove_path=True):
    """
    Creates a tar.gz of the path using the path basename + "tar.gz"
    The resulting file is in the parent directory of the original path, and
    the original path is removed.
    """
    root_path = os.path.dirname(path)
    relative_path = os.path.basename(path)
    archive_path = path + ".tar.gz"

    cmd = [["tar", "-C", root_path, "-czf", archive_path, relative_path]]
    call(cmd, env=SAFE_ENV)
    if remove_path:
        fs.remove(path)
    return archive_path


def generate_archive_name():
    """
    Creates the archive directory to store the component output.
    """
    hostname = determine_hostname()
    suffix = datetime.now(utc).strftime("%Y%m%d%H%M%S")
    return "insights-%s-%s" % (hostname, suffix)


def collect(
    client_config=None,
    rm_conf=None,
    tmp_path=None,
    archive_name=None,
    compress=False,
    manifest=None,
):
    """
    This is the collection entry point. It accepts a manifest, a temporary
    directory in which to store output, and a boolean for optional compression.

    Args:
        client_config (InsightsConfig): Configurations read from insights-client
            configuration, including "manifest".
        rm_conf (dict): Client-provided python dict containing keys
            "commands", "files", and "keywords", to be injected
            into the manifest blacklist.
        tmp_path (str): The temporary directory that is used to create a
            working directory for storing the final tar.gz if one is generated.
        archive_name (str): The directory that is used to generate the output
            as well as the final tar.gz.
        compress (boolean): True to create a tar.gz and remove the original
            workspace containing output. False to leave the workspace without
            creating a tar.gz
        manifest (str or dict): json document or dictionary containing the
            collection manifest. See default_manifest for an example.  This
            option works only for `insights-collect` where 'client_config'
            is not filled.

    Returns:
        (str, dict): The full path to the created tar.gz or workspace.
        And a dictionary with relevant exceptions captured by the broker during
        core collection, this dictionary has the following structure:
        ``{ exception_type: [ (exception_obj, component), (exception_obj, component) ]}``.
    """
    # Get the manifest per the following order:
    # 1. "client_config.manifest"
    # 2. "manifest" passed to the `insights.collect()`
    # 3. "default_manifest" defined in `insights.specs.manifests`
    manifest = manifests['default'] if manifest is None else manifest
    if client_config and hasattr(client_config, 'manifest') and client_config.manifest:
        manifest = client_config.manifest
    manifest = load_manifest(manifest)

    client = manifest.get("client", {})
    plugins = manifest.get("plugins", {})

    load_packages(plugins.get("packages", []))
    apply_default_enabled(plugins)
    apply_configs(plugins)
    # process blacklist
    black_list = client.get("blacklist", {})
    black_list.update(rm_conf or {})
    apply_blacklist(black_list)

    # insights-client
    if client_config and client_config.cmd_timeout:
        try:
            client['context']['args']['timeout'] = client_config.cmd_timeout
        except LookupError:
            log.warning('Could not set timeout option.')

    try:
        filters.load()
    except IOError as e:
        # could not load filters file
        log.debug("No filters available: %s", str(e))
    except AttributeError as e:
        # problem parsing the filters
        log.debug("Could not parse filters: %s", str(e))

    output_path = os.path.join(tmp_path, archive_name)
    fs.ensure_path(output_path)
    fs.touch(os.path.join(output_path, "insights_archive.txt"))

    broker = dr.Broker()
    ctx = create_context(client.get("context", {}))
    cleaner = Cleaner(client_config, black_list) if client_config else None
    broker[ctx.__class__] = ctx
    broker['cleaner'] = cleaner
    broker['redact_config'] = black_list
    broker['client_config'] = client_config

    # run in "serial" mode by default
    run_strategy = client.get("run_strategy", {"name": "serial"})
    parallel = run_strategy.get("name") == "parallel"
    to_persist = get_to_persist(client.get("persist", set()))

    if client_config and client_config.obfuscate and parallel:
        log.warning("Parallel collection is not supported when 'obfuscate' is enabled")
        parallel = False

    pool_args = run_strategy.get("args", {})
    with get_pool(parallel, "insights-collector-pool", pool_args) as pool:
        h = Hydration(output_path, ctx, pool=pool)
        broker.add_observer(h.make_persister(to_persist))
        dr.run_all(broker=broker, pool=pool)

    collect_errors = _parse_broker_exceptions(broker, EXCEPTIONS_TO_REPORT)

    cleaner.generate_report(archive_name) if cleaner else None

    if compress:
        return create_archive(output_path), collect_errors
    return output_path, collect_errors


def _parse_broker_exceptions(broker, exceptions_to_report):
    """
    Parse the exceptions captured in the broker during core collection
    and keep only exception types configured in the ``exceptions_to_report``.

    Args:
        broker (Broker): Broker object used for core collection.
        exceptions_to_report (set): Exception types to retrieve from the broker.

    Returns:
        (dict): A dictionary with relevant exceptions captured by the broker.
    """
    errors = {}
    try:
        if broker.exceptions:
            for component, exceptions in broker.exceptions.items():
                for ex in exceptions:
                    ex_type = type(ex)
                    if ex_type in exceptions_to_report:
                        if ex_type in errors.keys():
                            errors[ex_type].append((ex, component))
                        else:
                            errors[ex_type] = [(ex, component)]
    except Exception as e:
        log.warning("Could not parse exceptions from the broker.: %s", str(e))
    return errors


def main():
    # Remove command line args so that they are not parsed by any called modules
    # The main fxn is only invoked as a cli, if calling from another cli then
    # use the collect function instead
    collect_args = [arg for arg in sys.argv[1:]] if len(sys.argv) > 1 else []
    sys.argv = (
        [
            sys.argv[0],
        ]
        if sys.argv
        else sys.argv
    )

    p = argparse.ArgumentParser()
    p.add_argument("-m", "--manifest", help="Manifest yaml.")
    p.add_argument("-o", "--out_path", help="Path to write output data.")
    p.add_argument("-q", "--quiet", help="Error output only.", action="store_true")
    p.add_argument("-v", "--verbose", help="Verbose output.", action="store_true")
    p.add_argument("-d", "--debug", help="Debug output.", action="store_true")
    p.add_argument("-c", "--compress", help="Compress", action="store_true")
    args = p.parse_args(args=collect_args)

    level = logging.WARNING
    if args.verbose:
        level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    if args.quiet:
        level = logging.ERROR

    logging.basicConfig(level=level)

    out_path = args.out_path or tempfile.gettempdir()
    archive, errors = collect(
        manifest=args.manifest,
        tmp_path=out_path,
        archive_name=generate_archive_name(),
        compress=args.compress,
    )
    print(archive)


if __name__ == "__main__":
    main()
