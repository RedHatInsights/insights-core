"""
Utility functions
"""
from __future__ import absolute_import
import socket
import os
import fcntl
import logging
import uuid
import datetime
import shlex
import re
import stat
from subprocess import Popen, PIPE, STDOUT
from six.moves.configparser import RawConfigParser
import json

from .constants import InsightsConstants as constants

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

    return str(machine_id).strip()


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


def validate_remove_file(remove_file):
    """
    Validate the remove file
    """
    if not os.path.isfile(remove_file):
        logger.warn("WARN: Remove file does not exist")
        return False
    # Make sure permissions are 600
    mode = stat.S_IMODE(os.stat(remove_file).st_mode)
    if not mode == 0o600:
        logger.error("ERROR: Invalid remove file permissions"
                     "Expected 0600 got %s" % oct(mode))
        return False
    else:
        logger.debug("Correct file permissions")

    if os.path.isfile(remove_file):
        parsedconfig = RawConfigParser()
        parsedconfig.read(remove_file)
        rm_conf = {}
        for item, value in parsedconfig.items('remove'):
            rm_conf[item] = value.strip().split(',')
        # Using print here as this could contain sensitive information
        logger.debug("Remove file parsed contents")
        logger.debug(rm_conf)
    logger.info("JSON parsed correctly")
    return True


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

# MODIFY_JSON_FILE - Modify a JSON file in place.
#
# If the file doesn't exist initially, it is created with default
# permissions and the initial content is an empty JSON object.
#
# NAME: The name of the file to change
#
# MUTATE: A callback that does the modifications.  It will be called
#         with one argument, containing the old data from the file.
#         The function can modify this object directly and return
#         None.  Alternatively, the function can return a new object.
#
# Example mutator functions.  Note that the first preseves other
# fields in DATA while the second does not.
#
# def count_up(data):
#    if "count" in data:
#        data["count"] += 1
#    else:
#        data["count"] = 0
#
# def count_up_2(data):
#    return { "count": data["count"] + 1 if "count" in data else 0 }

def modify_json_file(name, mutate):
    f = os.fdopen(os.open(name, os.O_RDWR | os.O_CREAT, 0o666), 'r+')
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    old_text = f.read()
    old = { } if old_text == "" else json.loads(old_text)
    new = mutate(old) or old
    f.seek(0)
    f.truncate()
    f.write(json.dumps(new) + "\n")
    f.close()

# SET_IN_JSON_FILE - Set a field in a JSON file
#
# This is a convenience wrapper around MODIFY_JSON_FILE for the common
# case of this specific mutator function:
#
#  def mutate(data):
#      data[field] = value

def set_in_json_file(name, field, value):
    def mutate(data):
        data[field] = value
    modify_json_file(name, mutate)

def set_in_status_file(field, value):
    set_in_json_file(constants.status_file, field, value)

def delete_status_file():
    write_to_disk(constants.status_file, delete=True)
