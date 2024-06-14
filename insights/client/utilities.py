"""
Utility functions
"""
from __future__ import absolute_import
import glob
import os
import logging
import uuid
import datetime
import shlex
import re
import sys
import threading
import time
import json
import tarfile
import errno
from subprocess import Popen, PIPE, STDOUT

import yaml
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from .. import package_info
from .constants import InsightsConstants as constants
from .collection_rules import InsightsUploadConf, load_yaml
from insights.client import cert_auth

from insights.core.context import Context
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.util.hostname import determine_hostname  # noqa: F401

try:
    from insights_client.constants import InsightsConstants as wrapper_constants
except ImportError:
    wrapper_constants = None

logger = logging.getLogger(__name__)


def get_time():
    return datetime.datetime.isoformat(datetime.datetime.now())


def write_registered_file():
    delete_unregistered_file()
    for f in constants.registered_files:
        if os.path.lexists(f):
            if os.path.islink(f):
                # kill symlinks and regenerate
                os.remove(f)
                write_to_disk(f)
        else:
            write_to_disk(f)


def write_unregistered_file(date=None):
    """
    Write .unregistered out to disk
    """
    delete_registered_file()
    if date is None:
        date = get_time()
    for f in constants.unregistered_files:
        if os.path.lexists(f):
            if os.path.islink(f):
                # kill symlinks and regenerate
                os.remove(f)
                write_to_disk(f, content=str(date))
        else:
            write_to_disk(f, content=str(date))


def delete_registered_file():
    for f in constants.registered_files:
        write_to_disk(f, delete=True)


def delete_unregistered_file():
    for f in constants.unregistered_files:
        write_to_disk(f, delete=True)


def delete_cache_files():
    for f in glob.glob(os.path.join(constants.insights_core_lib_dir, "*.json")):
        os.remove(f)


def write_to_disk(filename, delete=False, content=None):
    """
    Write filename out to disk
    """
    if not os.path.exists(os.path.dirname(filename)):
        return
    if content is None:
        content = get_time()

    if delete:
        if os.path.lexists(filename):
            logger.debug("Removing '%s'" % filename)
            try:
                os.remove(filename)
            except OSError as err:
                # Only raise the exception if it's not
                # a missing file error (ENOENT), which can be
                # ignored since nothing needs to be removed.
                if err.errno != errno.ENOENT:
                    raise err
    else:
        logger.debug("Writing '%s'" % filename)
        with open(filename, 'wb') as f:
            f.write(content.encode('utf-8'))


def _get_rhsm_identity():
    """Get the subscription-manager identity certificate UUID.

    :returns: The subscription-manager UUID, or None if not found.
    :rtype: str | None
    """
    if cert_auth.RHSM_CONFIG is None:
        return None

    try:
        cert = cert_auth.rhsmCertificate.read()  # type: cert_auth.rhsmCertificate
        subscription_manager_uuid = cert.getConsumerId()  # type: str
    except Exception:
        return None

    logger.debug("Found subscription-manager UUID in '%s/%s'.", cert.PATH, cert.CERT)
    return subscription_manager_uuid


def generate_machine_id(new=False, destination_file=constants.machine_id_file):
    """Generate a machine-id if /etc/insights-client/machine-id does not exist.

    :param new: Force generate a new ID.
    :type new: bool
    :param destination_file: Path to the file the ID should be written to.
    :type destination_file: str

    :returns: The machine ID
    :rtype: str
    """
    machine_id = None  # type: str | None

    if os.path.isfile(destination_file) and not new:
        with open(destination_file, "r") as f:
            machine_id = f.read()
        logger.debug("Using existing machine-id: '%s'." % machine_id)

    if not machine_id:
        machine_id = _get_rhsm_identity()
        if machine_id:
            logger.debug("Using subscription-manager identity as machine-id: '%s'." % machine_id)
            write_to_disk(destination_file, content=machine_id)

    if not machine_id:
        machine_id = str(uuid.uuid4())
        logger.debug("Creating fresh machine-id: '%s'." % machine_id)
        write_to_disk(destination_file, content=machine_id)
    try:
        # Old versions (redhat-access-insights) could save the UUID without hyphens,
        # and that could mess up Inventory via e.g. `insights-client --check-results`.
        # See RHBZ#1998560 for more details.
        return str(uuid.UUID(str(machine_id).strip(), version=4))
    except ValueError as exc:
        logger.error("Invalid machine ID: '%s'." % machine_id)
        logger.error("Error details: %s", str(exc))
        logger.error("Please delete the file '%s' and rerun the client with '--register'." % destination_file)
        sys.exit(constants.sig_kill_bad)


def machine_id_exists(destination_file=constants.machine_id_file):
    """
    Get the machine-id or None if /etc/insights-client/machine-id it does not exists
    """
    return os.path.isfile(destination_file)


def _expand_paths(path):
    """
    Expand wildcarded paths
    """
    dir_name = os.path.dirname(path)
    paths = []
    logger.debug("Attempting to expand %s", path)
    if os.path.isdir(dir_name):
        files = os.listdir(dir_name)
        match = os.path.basename(path)
        for file_path in files:
            if re.match(match, file_path):
                expanded_path = os.path.join(dir_name, file_path)
                paths.append(expanded_path)
        logger.debug("Expanded paths %s", paths)
        return paths
    else:
        logger.debug("Could not expand %s", path)


def validate_remove_file(config):
    """
    Validate the remove file and tags file
    """
    return InsightsUploadConf(config).validate()


def write_data_to_file(data, filepath):
    '''
    Write data to file
    '''
    try:
        os.makedirs(os.path.dirname(filepath), 0o700)
    except OSError:
        pass

    write_to_disk(filepath, content=data)


def magic_plan_b(filename):
    '''
    Use this in instances where
    python-magic is MIA and can't be installed
    for whatever reason
    '''
    cmd = shlex.split('file --mime-type --mime-encoding ' + filename)
    stdout, stderr = Popen(cmd, stdout=PIPE).communicate()
    stdout = stdout.decode("utf-8")
    mime_str = stdout.split(filename + ': ')[1].strip()
    return mime_str


def run_command_get_output(cmd):
    proc = Popen(shlex.split(cmd),
                 stdout=PIPE, stderr=STDOUT)
    stdout, stderr = proc.communicate()

    return {
        'status': proc.returncode,
        'output': stdout.decode('utf-8', 'ignore')
    }


def modify_config_file(updates):
    '''
    Update the config file with certain things
    '''
    cmd = '/bin/sed '
    for key in updates:
        cmd = cmd + '-e \'s/^#*{key}.*=.*$/{key}={value}/\' '.format(key=key, value=updates[key])
    cmd = cmd + constants.default_conf_file
    status = run_command_get_output(cmd)
    write_to_disk(constants.default_conf_file, content=status['output'])


def get_version_info():
    '''
    Get the insights client and core versions for archival
    '''
    try:
        client_version = wrapper_constants.version
    except AttributeError:
        # wrapper_constants is None or has no attribute "version"
        client_version = None
    version_info = {}
    version_info['core_version'] = '%s-%s' % (package_info['VERSION'], package_info['RELEASE'])
    version_info['client_version'] = client_version
    return version_info


def print_egg_versions():
    '''
    Log all available eggs' versions
    '''
    versions = get_version_info()
    logger.debug('Client version: %s', versions['client_version'])
    logger.debug('Core version: %s', versions['core_version'])
    logger.debug('All egg versions:')
    eggs = [
        os.getenv('EGG'),
        '/var/lib/insights/newest.egg',
        '/var/lib/insights/last_stable.egg',
        '/etc/insights-client/rpm.egg',
    ]
    if not sys.executable:
        logger.debug('Python executable not found.')
        return

    for egg in eggs:
        if egg is None:
            logger.debug('ENV egg not defined.')
            continue
        if not os.path.exists(egg):
            logger.debug('%s not found.', egg)
            continue
        try:
            proc = Popen([sys.executable, '-c',
                         'from insights import package_info; print(\'%s-%s\' % (package_info[\'VERSION\'], package_info[\'RELEASE\']))'],
                         env={'PYTHONPATH': egg, 'PATH': os.getenv('PATH')}, stdout=PIPE, stderr=STDOUT)
        except OSError:
            logger.debug('Could not start python.')
            return
        stdout, stderr = proc.communicate()
        exit_code = proc.wait()

        if exit_code == 0:
            version = stdout.decode('utf-8', 'ignore').strip()
            logger.debug('%s: %s', egg, version)
        else:
            logger.debug('%s: Could not read egg version.', egg)


def read_pidfile():
    '''
    Read the pidfile we wrote at launch
    '''
    pid = None
    try:
        with open(constants.pidfile) as pidfile:
            pid = pidfile.read()
    except IOError:
        logger.debug('Could not open pidfile for reading.')
    return pid


def _systemd_notify(pid):
    '''
    Ping the systemd watchdog with the main PID so that
    the watchdog doesn't kill the process
    '''
    try:
        proc = Popen(['/usr/bin/systemd-notify', '--pid=' + str(pid), 'WATCHDOG=1'])
    except OSError as e:
        logger.debug('Could not launch systemd-notify: %s', str(e))
        return False
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        logger.debug('systemd-notify returned %s', proc.returncode)
        return False
    return True


def systemd_notify_init_thread():
    '''
    Use a thread to periodically ping systemd instead
    of calling it on a per-command basis
    '''
    pid = read_pidfile()
    if not pid:
        logger.debug('No PID specified.')
        return
    if not os.getenv('NOTIFY_SOCKET'):
        # running standalone, not via systemd job
        return
    if not os.path.exists('/usr/bin/systemd-notify'):
        # RHEL 6, no systemd
        return

    def _sdnotify_loop():
        while True:
            # run sdnotify every 30 seconds
            if not _systemd_notify(pid):
                # end the loop if something goes wrong
                break
            time.sleep(30)

    sdnotify_thread = threading.Thread(target=_sdnotify_loop, args=())
    sdnotify_thread.daemon = True
    sdnotify_thread.start()


def get_tags(tags_file_path=constants.default_tags_file):
    '''
    Load tag data from the tags file.

    Returns: a dict containing tags defined on the host.
    '''
    tags = None

    if os.path.isfile(tags_file_path):
        try:
            tags = load_yaml(tags_file_path)
        except RuntimeError:
            logger.error("Invalid YAML. Unable to load %s", tags_file_path)
            return None
    else:
        logger.debug("%s does not exist", tags_file_path)

    return tags


def write_tags(tags, tags_file_path=constants.default_tags_file):
    """
    Writes tags to tags_file_path

    Arguments:
      - tags (dict): the tags to write
      - tags_file_path (string): path to which tag data will be written

    Returns: None
    """
    with open(tags_file_path, mode="w") as f:
        data = yaml.dump(tags, Dumper=Dumper, default_flow_style=False)
        f.write(data)


def migrate_tags():
    '''
    We initially released the tags feature with the tags file set as
    tags.conf, but soon after switched it over to tags.yaml. There may be
    installations out there with tags.conf files, so rename the files.
    '''
    tags_conf = os.path.join(constants.default_conf_dir, 'tags.conf')
    tags_yaml = os.path.join(constants.default_conf_dir, 'tags.yaml')

    if os.path.exists(tags_yaml):
        # current default file exists, do nothing
        return
    if os.path.exists(tags_conf):
        # old file exists and current does not
        logger.info('Tags file %s detected. This filename is deprecated; please use %s. The file will be renamed automatically.',
                    tags_conf, tags_yaml)
        try:
            os.rename(tags_conf, tags_yaml)
        except OSError as e:
            logger.error(e)


def get_parent_process():
    '''
    Get parent process of the client

    Returns: string
    '''
    ppid = os.getppid()
    output = run_command_get_output('cat /proc/%s/status' % ppid)
    if output['status'] == 0:
        name = output['output'].splitlines()[0].split('\t')[1]
        return name
    else:
        return "unknown"


def os_release_info():
    '''
    Use insights-core to fetch the os-release or redhat-release info

    Returns a tuple of OS name and version
    '''
    os_family = "Unknown"
    os_release = ""
    for p in ["/etc/os-release", "/etc/redhat-release"]:
        try:
            with open(p) as f:
                data = f.readlines()

            ctx = Context(content=data, path=p, relative_path=p)
            if p == "/etc/os-release":
                rls = OsRelease(ctx)
                os_family = rls.data.get("NAME")
                os_release = rls.data.get("VERSION_ID")
            elif p == "/etc/redhat-release":
                rls = RedhatRelease(ctx)
                os_family = rls.product
                os_release = rls.version
            break
        except IOError:
            continue
        except Exception as e:
            logger.warning("Failed to detect OS version: %s", e)
    return (os_family, os_release)


def largest_spec_in_archive(archive_file):
    logger.info("Checking for large files...")
    tar_file = tarfile.open(archive_file, 'r')
    largest_fsize = 0
    largest_file_name = ""
    largest_spec = ""
    # get the name of the archive
    name = os.path.basename(archive_file).split(".tar.gz")[0]
    # get the archives from inside meta_data directory
    metadata_top = os.path.join(name, "meta_data/")
    data_top = os.path.join(name, "data")
    for file in tar_file.getmembers():
        if metadata_top in file.name:
            file_extract = tar_file.extractfile(file.name)
            specs_metadata = json.load(file_extract)
            results = specs_metadata.get("results", [])
            if not results:
                continue
            if not isinstance(results, list):
                # specs with only one resulting file are not in list form
                results = [results]
            for result in results:
                # get the path of the spec result and check its filesize
                fname = result.get("object", {}).get("relative_path")
                abs_fname = os.path.join('.', data_top, fname)
                # get the archives from inside data directory
                data_file = tar_file.getmember(abs_fname)
                if (data_file.size > largest_fsize):
                    largest_fsize = data_file.size
                    largest_file_name = fname
                    largest_spec = specs_metadata["name"]
    return (largest_file_name, largest_fsize, largest_spec)


def size_in_mb(num_bytes):
    return float(num_bytes) / (1024 * 1024)
