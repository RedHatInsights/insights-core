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
from insights.core.serde import Hydration
from insights.core.spec_cleaner import Cleaner
from insights.util import fs
from insights.util.hostname import determine_hostname
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

    # needed for the ausearch_insights_client
        - name: insights.components.rhel_version.IsGtOrRhel86
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
        - name: insights.components.rhel_version.IsRhel6
          enabled: true

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

        - name: insights.parsers.httpd_conf.HttpdConf
          enabled: true

    # needed for httpd_on_nfs
        - name: insights.parsers.mount.ProcMounts
          enabled: true

    # needed for nginx_ssl_cert_enddate
        - name: insights.combiners.nginx_conf.NginxConfTree
          enabled: true

        - name: insights.parsers.nginx_conf.NginxConfPEG
          enabled: true

    # needed for mssql_tls_cert_enddate
        - name: insights.parsers.mssql_conf.MsSQLConf
          enabled: true

    # need for rsyslog_tls_cert_file
        - name: insights.parsers.rsyslog_conf.RsyslogConf
          enabled: true

        - name: insights.combiners.rsyslog_confs.RsyslogAllConf
          enabled: true

    # needed to collect the sap_hdb_version spec that uses the Sap combiner
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
        - name: insights.components.satellite.IsSatellite614AndLater
          enabled: true
        - name: insights.components.satellite.IsSatelliteLessThan614
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
    suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return "insights-%s-%s" % (hostname, suffix)


def collect(client_config=None, rm_conf=None, tmp_path=None,
            archive_name=None, compress=False, manifest=None):
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
    # 3. "default_manifest" defined in this module
    manifest = default_manifest if manifest is None else manifest
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

    cleaner.generate_report(archive_name, client_config.rhsm_facts_file) if cleaner else None

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

    out_path = args.out_path or tempfile.gettempdir()
    archive, errors = collect(manifest=args.manifest, tmp_path=out_path,
                              archive_name=generate_archive_name(),
                              compress=args.compress)
    print(archive)


if __name__ == "__main__":
    main()
