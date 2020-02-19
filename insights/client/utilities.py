"""
Utility functions
"""
from __future__ import absolute_import
import socket
import os
import logging
import uuid
import datetime
import shlex
import re
import sys
from subprocess import Popen, PIPE, STDOUT

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .. import package_info
from .constants import InsightsConstants as constants
from .collection_rules import InsightsUploadConf

logger = logging.getLogger(__name__)


def determine_hostname(display_name=None):
    """
    Find fqdn if we can
    """
    if display_name:
        # if display_name is provided, just return the given name
        return display_name
    else:
        socket_gethostname = socket.gethostname()
        socket_fqdn = socket.getfqdn()

        try:
            socket_ex = socket.gethostbyname_ex(socket_gethostname)[0]
        except (LookupError, socket.gaierror):
            socket_ex = ''

        gethostname_len = len(socket_gethostname)
        fqdn_len = len(socket_fqdn)
        ex_len = len(socket_ex)

        if fqdn_len > gethostname_len or ex_len > gethostname_len:
            if "localhost" not in socket_ex and len(socket_ex):
                return socket_ex
            if "localhost" not in socket_fqdn:
                return socket_fqdn

        return socket_gethostname


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
    # this function only called when machine is registered,
    #  so while registering, delete this file too. we only
    #  need it around until we're registered
    write_to_disk(constants.register_marker_file, delete=True)


def write_to_disk(filename, delete=False, content=get_time()):
    """
    Write filename out to disk
    """
    if not os.path.exists(os.path.dirname(filename)):
        return
    if delete:
        if os.path.lexists(filename):
            os.remove(filename)
    else:
        with open(filename, 'wb') as f:
            f.write(content.encode('utf-8'))


def generate_machine_id(new=False,
                        destination_file=constants.machine_id_file):
    """
    Generate a machine-id if /etc/insights-client/machine-id does not exist
    """
    machine_id = None
    machine_id_file = None
    logging_name = 'machine-id'

    if os.path.isfile(destination_file) and not new:
        logger.debug('Found %s', destination_file)
        with open(destination_file, 'r') as machine_id_file:
            machine_id = machine_id_file.read()
    else:
        logger.debug('Could not find %s file, creating', logging_name)
        machine_id = str(uuid.uuid4())
        logger.debug("Creating %s", destination_file)
        write_to_disk(destination_file, content=machine_id)

    try:
        uuid.UUID(machine_id, version=4)
        return str(machine_id).strip()
    except ValueError:
        logger.error("Invalid machine ID: %s", machine_id)
        logger.error("Remove %s and a new one will be generated.\nRerun the client with --register", destination_file)
        sys.exit(constants.sig_kill_bad)


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
    Validate the remove file
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
    cmd = 'rpm -q --qf "%{VERSION}-%{RELEASE}" insights-client'
    version_info = {}
    version_info['core_version'] = '%s-%s' % (package_info['VERSION'], package_info['RELEASE'])
    rpm_proc = run_command_get_output(cmd)
    if rpm_proc['status'] != 0:
        # Unrecoverable error
        logger.debug('Error occurred while running rpm -q. Details:\n%s' % rpm_proc['output'])
        version_info['client_version'] = None
    else:
        version_info['client_version'] = rpm_proc['output']
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
        version = stdout.decode('utf-8', 'ignore').strip()
        logger.debug('%s: %s', egg, version)


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


def systemd_notify(pid):
    '''
    Ping the systemd watchdog with the main PID so that
    the watchdog doesn't kill the process
    '''
    if not os.getenv('NOTIFY_SOCKET'):
        # running standalone, not via systemd job
        return
    if not pid:
        logger.debug('No PID specified.')
        return
    if not os.path.exists('/usr/bin/systemd-notify'):
        # RHEL 6, no systemd
        return
    try:
        proc = Popen(['/usr/bin/systemd-notify', '--pid=' + str(pid), 'WATCHDOG=1'])
    except OSError:
        logger.debug('Could not launch systemd-notify.')
        return
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        logger.debug('systemd-notify returned %s', proc.returncode)


def get_tags(tags_file_path=os.path.join(constants.default_conf_dir, "tags.conf")):
    '''
    Load tag data from the tags file.

    Returns: a dict containing tags defined on the host.
    '''
    tags = None

    try:
        with open(tags_file_path) as f:
            data = f.read()
            tags = yaml.load(data, Loader=Loader)
    except EnvironmentError as e:
        logger.debug("tags file does not exist: %s", os.strerror(e.errno))

    return tags


def write_tags(tags, tags_file_path=os.path.join(constants.default_conf_dir, "tags.conf")):
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
