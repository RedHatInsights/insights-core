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
from insights.core import blacklist, dr, filters
from insights.core.blacklist import BLACKLISTED_SPECS
from insights.core.exceptions import CalledProcessError
from insights.core.serde import Hydration
from insights.util import fs
from insights.util.subproc import call

SAFE_ENV = {
    "PATH": os.path.pathsep.join([
        "/bin",
        "/usr/bin",
        "/sbin",
        "/usr/sbin",
        "/usr/share/Modules/bin",
    ]),
    "LC_ALL": "C",
}

if "LANG" in os.environ:
    SAFE_ENV["LANG"] = os.environ["LANG"]

log = logging.getLogger(__name__)

default_manifest = """
---
# version is for the format of this file, not its contents.
version: 0

client:
    context:
        class: insights.core.context.HostContext
        args:
            timeout: 10 # timeout in seconds for commands. Doesn't apply to files.

    # commands and files to ignore
    blacklist:
        files: []
        commands: []
        patterns: []
        keywords: []

    # Can be a list of dictionaries with name/enabled fields or a list of strings
    # where the string is the name and enabled is assumed to be true. Matching is
    # by prefix, and later entries override previous ones. Persistence for a
    # component is disabled by default.
    persist:
        - name: insights.specs.Specs
          enabled: true

    run_strategy:
        name: serial
        args:
            max_workers: null

plugins:
    # disable everything by default
    # defaults to false if not specified.
    default_component_enabled: false

    # packages and modules to load
    packages:
        - insights.specs.default
        - insights.specs.datasources

    # configuration of loaded components. names are prefixes, so any component with
    # a fully qualified name that starts with a key will get the associated
    # configuration applied. Can specify timeout, which will apply to command
    # datasources. Can specify metadata, which must be a dictionary and will be
    # merged with the components' default metadata.
    configs:
        - name: insights.specs.datasources
          enabled: true

        - name: insights.specs.Specs
          enabled: true

        - name: insights.specs.default.DefaultSpecs
          enabled: true

        - name: insights.parsers.hostname
          enabled: true

        - name: insights.parsers.systemid
          enabled: true

        - name: insights.combiners.hostname
          enabled: true

    # needed for the CloudProvider combiner
        - name: insights.parsers.installed_rpms
          enabled: true

        - name: insights.parsers.dmidecode
          enabled: true

        - name: insights.parsers.yum
          enabled: true

        - name: insights.parsers.rhsm_conf
          enabled: true

        - name: insights.combiners.cloud_provider
          enabled: true

    # needed for the cloud related specs
        - name: insights.components.cloud_provider.IsAWS
          enabled: true

        - name: insights.components.cloud_provider.IsAzure
          enabled: true

        - name: insights.components.cloud_provider.IsGCP
          enabled: true

    # needed for the ceph related specs
        - name: insights.components.ceph.IsCephMonitor
          enabled: true

    # needed for the Services combiner
        - name: insights.parsers.chkconfig
          enabled: true

        - name: insights.parsers.systemd.unitfiles
          enabled: true

        - name: insights.combiners.services
          enabled: true

    # needed for the 'teamdctl_state_dump' spec
        - name: insights.parsers.nmcli.NmcliConnShow
          enabled: true

    # needed for multiple Datasouce specs
        - name: insights.parsers.ps.PsAuxcww
          enabled: true

        - name: insights.parsers.ps.PsAuxww
          enabled: true

        - name: insights.combiners.ps
          enabled: true

    # needed for httpd_certificate
        - name: insights.combiners.httpd_conf.HttpdConfTree
          enabled: true

        - name: insights.combiners.httpd_conf._HttpdConf
          enabled: true

    # needed for httpd_on_nfs
        - name: insights.parsers.mount.ProcMounts
          enabled: true

    # needed for nginx_ssl_cert_enddate
        - name: insights.combiners.nginx_conf.NginxConfTree
          enabled: true

        - name: insights.combiners.nginx_conf._NginxConf
          enabled: true

    # needed for mssql_tls_cert_enddate
        - name: insights.parsers.mssql_conf.MsSQLConf
          enabled: true

    # needed to collect the sap_hdb_version spec that uses the Sap combiner
        - name: insights.parsers.lssap
          enabled: true

        - name: insights.parsers.saphostctrl
          enabled: true

        - name: insights.combiners.sap
          enabled: true

    # needed for fw_devices and fw_security specs
        - name: insights.parsers.dmidecode.DMIDecode
          enabled: true

        - name: insights.parsers.virt_what.VirtWhat
          enabled: true

        - name: insights.combiners.virt_what.VirtWhat
          enabled: true

        - name: insights.components.virtualization.IsBareMetal
          enabled: true

    # needed for the 'pre-check' of the 'ss' spec and the 'modinfo_filtered_modules' spec
        - name: insights.parsers.lsmod.LsMod
          enabled: true

    # needed for the 'pre-check' of the 'is_satellite_server' spec
        - name: insights.combiners.satellite_version.SatelliteVersion
          enabled: true
        - name: insights.components.satellite.IsSatellite
          enabled: true

    # needed for the 'pre-check' of the 'is_satellite_capsule' spec
        - name: insights.combiners.satellite_version.CapsuleVersion
          enabled: true
        - name: insights.components.satellite.IsCapsule
          enabled: true

    # needed for the 'pre-check' of the 'satellite_provision_param_settings' spec
        - name: insights.components.satellite.IsSatellite611
          enabled: true

    # needed for the 'pre-check' of the 'corosync_cmapctl_cmd_list' spec
        - name: insights.combiners.redhat_release.RedHatRelease
          enabled: true
        - name: insights.parsers.uname.Uname
          enabled: true
        - name: insights.parsers.redhat_release.RedhatRelease
          enabled: true
        - name: insights.components.rhel_version.IsRhel7
          enabled: true
        - name: insights.components.rhel_version.IsRhel8
          enabled: true
        - name: insights.components.rhel_version.IsRhel9
          enabled: true

    # needed for the 'pmlog_summary' spec
        - name: insights.parsers.ros_config.RosConfig
          enabled: true

    # needed for the 'container' specs
        - name: insights.parsers.podman_list.PodmanListContainers
          enabled: true

        - name: insights.parsers.docker_list.DockerListContainers
          enabled: true

    # needed because some specs aren't given names before they're used in DefaultSpecs
        - name: insights.core.spec_factory
          enabled: true

    # needed by the 'luks_data_sources' spec
        - name: insights.parsers.blkid.BlockIDInfo
          enabled: true

        - name: insights.components.cryptsetup
          enabled: true

    # needed by the 'iris_cpf' spec
        - name: insights.parsers.iris.IrisList
          enabled: true

    # needed by the 'iris_messages_log' spec
        - name: insights.parsers.iris.IrisCpf
          enabled: true
""".strip()

EXCEPTIONS_TO_REPORT = set([
    OSError
])
"""Exception types that should be reported on after core collection."""


def load_manifest(data):
    """ Helper for loading a manifest yaml doc. """
    if isinstance(data, dict):
        return data
    doc = yaml.safe_load(data)
    if not isinstance(doc, dict):
        raise Exception("Manifest didn't result in dict.")
    return doc


def load_packages(pkgs):
    for p in pkgs:
        dr.load_components(p, continue_on_error=False)


def apply_blacklist(cfg):
    for b in cfg.get("files", []):
        blacklist.add_file(b)

    for b in cfg.get("commands", []):
        blacklist.add_command(b)

    for b in cfg.get("patterns", []):
        blacklist.add_pattern(b)

    for b in cfg.get("keywords", []):
        blacklist.add_keyword(b)


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


def collect(manifest=default_manifest, tmp_path=None, compress=False,
            rm_conf=None, client_config=None):
    """
    This is the collection entry point. It accepts a manifest, a temporary
    directory in which to store output, and a boolean for optional compression.

    Args:
        manifest (str or dict): json document or dictionary containing the
            collection manifest. See default_manifest for an example.
        tmp_path (str): The temporary directory that will be used to create a
            working directory for storing component output as well as the final
            tar.gz if one is generated.
        compress (boolean): True to create a tar.gz and remove the original
            workspace containing output. False to leave the workspace without
            creating a tar.gz
        rm_conf (dict): Client-provided python dict containing keys
            "commands", "files", and "keywords", to be injected
            into the manifest blacklist.
        client_config (InsightsConfig): Configurations read by the client tool.
    Returns:
        (str, dict): The full path to the created tar.gz or workspace.
        And a dictionary with relevant exceptions captured by the broker during
        core collection, this dictionary has the following structure:
        ``{ exception_type: [ (exception_obj, component), (exception_obj, component) ]}``.
    """

    manifest = load_manifest(manifest)
    client = manifest.get("client", {})
    plugins = manifest.get("plugins", {})
    run_strategy = client.get("run_strategy", {"name": "parallel"})

    load_packages(plugins.get("packages", []))
    apply_default_enabled(plugins)
    apply_configs(plugins)

    apply_blacklist(client.get("blacklist", {}))

    # insights-client
    if client_config and client_config.cmd_timeout:
        try:
            client['context']['args']['timeout'] = client_config.cmd_timeout
        except LookupError:
            log.warning('Could not set timeout option.')
    rm_conf = rm_conf or {}
    apply_blacklist(rm_conf)
    for component in rm_conf.get('components', []):
        if not dr.get_component_by_name(component):
            log.warning('WARNING: Unknown component in blacklist: %s' % component)
        else:
            dr.set_enabled(component, enabled=False)
            BLACKLISTED_SPECS.append(component.split('.')[-1])
            log.warning('WARNING: Skipping component: %s', component)

    to_persist = get_to_persist(client.get("persist", set()))

    try:
        filters.load()
    except IOError as e:
        # could not load filters file
        log.debug("No filters available: %s", str(e))
    except AttributeError as e:
        # problem parsing the filters
        log.debug("Could not parse filters: %s", str(e))

    try:
        hostname = call("hostname -f", env=SAFE_ENV).strip()
    except CalledProcessError:
        # problem calling hostname -f
        hostname = call("hostname", env=SAFE_ENV).strip()
    suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    relative_path = "insights-%s-%s" % (hostname, suffix)
    tmp_path = tmp_path or tempfile.gettempdir()
    output_path = os.path.join(tmp_path, relative_path)
    fs.ensure_path(output_path)
    fs.touch(os.path.join(output_path, "insights_archive.txt"))

    broker = dr.Broker()
    ctx = create_context(client.get("context", {}))
    broker[ctx.__class__] = ctx
    broker['client_config'] = client_config

    parallel = run_strategy.get("name") == "parallel"
    pool_args = run_strategy.get("args", {})
    with get_pool(parallel, "insights-collector-pool", pool_args) as pool:
        h = Hydration(output_path, pool=pool)
        broker.add_observer(h.make_persister(to_persist))
        dr.run_all(broker=broker, pool=pool)

    collect_errors = _parse_broker_exceptions(broker, EXCEPTIONS_TO_REPORT)

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
    sys.argv = [sys.argv[0], ] if sys.argv else sys.argv

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

    if args.manifest:
        with open(args.manifest) as f:
            manifest = f.read()
    else:
        manifest = default_manifest

    out_path = args.out_path or tempfile.gettempdir()
    archive, errors = collect(manifest, out_path, compress=args.compress)
    print(archive)


if __name__ == "__main__":
    main()
