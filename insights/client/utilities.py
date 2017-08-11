"""
Utility functions
"""
import socket
import os
import logging
import uuid
import datetime
import shlex
import re
import stat
import json
from subprocess import Popen, PIPE, STDOUT
from insights.contrib.ConfigParser import RawConfigParser

from constants import InsightsConstants as constants

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


def write_unregistered_file(date=None):
    """
    Write .unregistered out to disk
    """
    write_to_disk(constants.registered_file, delete=True)
    rc = 0
    if date is None:
        date = get_time()
    else:
        rc = 1

    write_to_disk(constants.unregistered_file, content=str(date))
    return rc


def write_to_disk(filename, delete=False, content=get_time()):
    """
    Write filename out to disk
    """
    if delete:
        if os.path.isfile(filename):
            os.remove(filename)
    else:
        with open(filename, 'w') as f:
            f.write(content)


def generate_machine_id(new=False,
                        docker_group=False,
                        destination_file=constants.machine_id_file):
    """
    Generate a machine-id if /etc/insights-client/machine-id does not exist
    """
    machine_id = None
    machine_id_file = None
    logging_name = 'machine-id'
    if docker_group:
        # generate a docker group ("docking station") id
        #   for the API to parse this group of systems
        destination_file = constants.docker_group_id_file
        logging_name = 'docker-group-id'
    if os.path.isfile(destination_file) and not new:
        logger.debug('Found %s', destination_file)
        with open(destination_file, 'r') as machine_id_file:
            machine_id = machine_id_file.read()
    else:
        logger.debug('Could not find %s file, creating', logging_name)
        machine_id = str(uuid.uuid4())
        logger.debug("Creating %s", destination_file)
        write_to_disk(destination_file, content=machine_id)

    # update the ansible machine id facts file
    if os.path.isdir(constants.insights_ansible_facts_dir):
        if not (os.path.isfile(constants.insights_ansible_machine_id_file) and machine_id) or new:
            machine_id_json = {'machine-id': machine_id}
            with open(constants.insights_ansible_machine_id_file, 'w') as handler:
                logger.debug('Writing Ansible machine-id facts file %s', constants.insights_ansible_machine_id_file)
                handler.write(json.dumps(machine_id_json))

    return str(machine_id).strip()


def generate_analysis_target_id(analysis_target, name):
    # this function generates 'machine-id's for analysis target's that
    # might not be hosts.
    #
    # 'machine_id' is what Insights uses to uniquely identify
    # the thing-to-be-analysed.  Primarily it determines when two uploads
    # are for the 'same thing', and so the latest upload should update the
    # later one Up till now that has only been hosts (machines), and so a
    # random uuid (uuid4) machine-id was generated for the host as its machine-id,
    # and written to a file on the host, and reused for all insights
    # uploads for that host.
    #
    # For docker images and containers, it will be difficult to impossible
    # to save their machine id's anywhere.  Also, while containers change
    # over time just like hosts, images don't change over time, though they
    # can be rebuilt.  So for images we want the 'machine-id' for an 'image'
    # to follow the rebuilt image, not change every time the image is rebuilt.
    # Typically when an image is rebuilt, the rebuilt image will have the same
    # name as its predicessor, but a different version (tag).
    #
    # So for images and containers, instead of random uuids, we use namespace uuids
    # (uuid5's).  This generates a new uuid based on a combination of another
    # uuid, and a name (a character string).  This will always generate the
    # same uuid for the same given base uuid and name.  This saves us from
    # having to save the image's uuid anywhere, and lets us control the created uuid
    # by controlling the name used to generate it.  Keep the name and base uuid) the
    # same, we get the same uuid.
    #
    # For the base uuid we use the uuid of the host we are running on.
    # For containers this is the obvious choice, for images it is less obviously
    # what base uuid is correct.  For now we will just go with the host's uuid also.
    #
    # For the name, we leave that outside this function, but in general it should
    # be the name of the container or the name of the image, and if you want to
    # replace the results on the insights server, you have to use the same name

    if analysis_target == "host":
        return generate_machine_id()
    elif (analysis_target == "docker_image" or
            analysis_target == "docker_container" or
            analysis_target == "compressed_file" or
            analysis_target == "mountpoint"):
        return generate_container_id(name)
    else:
        raise ValueError("Unknown analysis target: %s" % analysis_target)


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


def validate_remove_file(remove_file=constants.collection_remove_file):
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

    write_to_disk(filepath, content=data.encode('utf8'))


def magic_plan_b(filename):
    '''
    Use this in instances where
    python-magic is MIA and can't be installed
    for whatever reason
    '''
    cmd = shlex.split('file --mime-type --mime-encoding ' + filename)
    stdout, stderr = Popen(cmd, stdout=PIPE).communicate()
    mime_str = stdout.split(filename + ': ')[1].strip()
    return mime_str


def generate_container_id(container_name):
    # container id is a uuid in the namespace of the machine
    return str(uuid.uuid5(uuid.UUID(generate_machine_id()), container_name.encode('utf8')))


def run_command_get_output(cmd):
    proc = Popen(shlex.split(cmd.encode("utf-8")),
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
