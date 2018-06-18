#!/usr/bin/python

# The following is so that insights-client continues to work normally in places where
# Docker is not installed.
#
# Note that this is actually testing if the python docker client is importable (is installed),
# and if the docker server on this machine is accessable, which isn't exactly the
# same thing as 'there is no docker on this machine'.

from __future__ import absolute_import
import os
import logging
import shlex
import subprocess
import sys

from .constants import InsightsConstants as constants

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


def run_command_very_quietly(cmdline):  # shhhhhhhh
    # this takes a string (not an array)
    # need to redirect stdout and stderr to /dev/null
    with open(os.devnull, 'w') as devnull:
        cmd = shlex.split(cmdline.encode('utf8'))
        proc = subprocess.Popen(cmd, stdout=devnull, stderr=subprocess.STDOUT)
        returncode = proc.wait()
        return returncode


# only run docker commands OR atomic commands
# defaults to atomic (if present)
UseAtomic = True
UseDocker = False

# Check to see if we have access to docker
HaveDocker = False
HaveDockerException = None
try:
    if run_command_very_quietly("which docker") == 0:
        # a returncode of 0 means cmd ran correctly
        HaveDocker = True
except Exception as e:
    HaveDockerException = e

# Check to see if we have access to Atomic through the 'atomic' command
HaveAtomic = False
HaveAtomicException = None
try:
    if run_command_very_quietly("which atomic") == 0:
        # a returncode of 0 means cmd ran correctly
        HaveAtomic = True
    else:
        # anything else indicates problem
        HaveAtomic = False
except Exception as e:
    # this happens when atomic isn't installed or is otherwise unrunable
    HaveAtomic = False
    HaveAtomicException = e
HaveAtomicMount = HaveAtomic


# failsafe for if atomic / docker is/isnt present
if not HaveAtomic and HaveDocker:
    UseDocker = True
    UseAtomic = False
if not HaveDocker and HaveAtomic:
    UseAtomic = True
    UseDocker = False

# # force atomic or docker
# if config.use_docker:
#     UseAtomic = False
#     UseDocker = True
# if config.use_atomic:
#     UseAtomic = True
#     UseDocker = False

# Check if docker is running
DockerIsRunning = False
try:
    if run_command_very_quietly("docker info") == 0:
        # a returncode of 0 means cmd ran correctly
        DockerIsRunning = True
except Exception as e:
    HaveDockerException = e

# if HaveDocker:
if ((DockerIsRunning and UseDocker and HaveDocker) or
        (DockerIsRunning and UseAtomic and HaveAtomic)):
    import tempfile
    import shutil
    import json

    def runcommand(cmd):
        # this takes an array (not a string)
        logger.debug("Running Command: %s" % cmd)
        proc = subprocess.Popen(cmd)
        returncode = proc.wait()
        return returncode

    def run_command_capture_output(cmdline):
        cmd = shlex.split(cmdline.encode('utf8'))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        return out

    def use_atomic_run():
        return UseAtomic and HaveAtomic

    def use_atomic_mount():
        return UseAtomic and HaveAtomicMount

    def pull_image(image):
        return runcommand(shlex.split("docker pull") + [image])

    def get_targets(config):
        targets = []
        logger.debug('Getting targets to scan...')
        for d in _docker_all_image_ids():
            logger.debug('Checking if %s equals %s.' % (d, config.analyze_image_id))
            # pull the sha256: off the id to compare short IDs
            if (config.analyze_image_id == d or
               d.split('sha256:')[-1].startswith(config.analyze_image_id)):
                logger.debug('%s equals %s' % (d, config.analyze_image_id))
                targets.append({'type': 'docker_image', 'name': d})
                return targets  # return the first one that matches
        logger.debug('Done collecting targets')
        logger.debug(targets)
        if len(targets) == 0:
            logger.error("There was an error collecting targets. No image was found matching this ID.")
            sys.exit(constants.sig_kill_bad)
        return targets

    class AtomicTemporaryMountPoint:
        # this is used for both images and containers

        def __init__(self, image_id, mount_point):
            self.image_id = image_id
            self.mount_point = mount_point

        def get_fs(self):
            return self.mount_point

        def close(self):
            try:
                logger.debug("Closing Id %s On %s" % (self.image_id, self.mount_point))
                runcommand(shlex.split("atomic unmount") + [self.mount_point])
            except Exception as e:
                logger.debug("exception while unmounting image or container: %s" % e)
            shutil.rmtree(self.mount_point, ignore_errors=True)

    from .mount import DockerMount, Mount

    class DockerTemporaryMountPoint:
        # this is used for both images and containers

        def __init__(self, driver, image_id, mount_point, cid):
            self.driver = driver
            self.image_id = image_id
            self.mount_point = mount_point
            self.cid = cid

        def get_fs(self):
            return self.mount_point

        def close(self):
            try:
                logger.debug("Closing Id %s On %s" % (self.image_id, self.mount_point))
                # If using device mapper, unmount the bind-mount over the directory
                if self.driver == 'devicemapper':
                    Mount.unmount_path(self.mount_point)

                DockerMount(self.mount_point).unmount(self.cid)
            except Exception as e:
                logger.debug("exception while unmounting image or container: %s" % e)
            shutil.rmtree(self.mount_point, ignore_errors=True)

    def open_image(image_id):
        global HaveAtomicException
        if HaveAtomicException and UseAtomic:
            logger.debug("atomic is either not installed or not accessable %s" %
                         HaveAtomicException)
            HaveAtomicException = None

        if use_atomic_mount():
            mount_point = tempfile.mkdtemp()
            logger.debug("Opening Image Id %s On %s using atomic" % (image_id, mount_point))
            if runcommand(shlex.split("atomic mount") + [image_id, mount_point]) == 0:
                return AtomicTemporaryMountPoint(image_id, mount_point)
            else:
                logger.error('Could not mount Image Id %s On %s' % (image_id, mount_point))
                shutil.rmtree(mount_point, ignore_errors=True)
                return None

        else:
            driver = _docker_driver()
            if driver is None:
                return None

            mount_point = tempfile.mkdtemp()
            logger.debug("Opening Image Id %s On %s using docker client" % (image_id, mount_point))
            # docker mount creates a temp image
            # we have to use this temp image id to remove the device
            mount_point, cid = DockerMount(mount_point).mount(image_id)
            if driver == 'devicemapper':
                DockerMount.mount_path(os.path.join(mount_point, "rootfs"), mount_point, bind=True)
            if cid:
                return DockerTemporaryMountPoint(driver, image_id, mount_point, cid)
            else:
                logger.error('Could not mount Image Id %s On %s' % (image_id, mount_point))
                shutil.rmtree(mount_point, ignore_errors=True)
                return None

    def open_container(container_id):
        global HaveAtomicException
        if HaveAtomicException and UseAtomic:
            logger.debug("atomic is either not installed or not accessable %s" %
                         HaveAtomicException)
            HaveAtomicException = None

        if use_atomic_mount():
            mount_point = tempfile.mkdtemp()
            logger.debug("Opening Container Id %s On %s using atomic" %
                         (container_id, mount_point))
            if runcommand(shlex.split("atomic mount") + [container_id, mount_point]) == 0:
                return AtomicTemporaryMountPoint(container_id, mount_point)
            else:
                logger.error('Could not mount Container Id %s On %s' % (container_id, mount_point))
                shutil.rmtree(mount_point, ignore_errors=True)
                return None

        else:
            driver = _docker_driver()
            if driver is None:
                return None

            mount_point = tempfile.mkdtemp()
            logger.debug("Opening Container Id %s On %s using docker client" %
                         (container_id, mount_point))
            # docker mount creates a temp image
            # we have to use this temp image id to remove the device
            mount_point, cid = DockerMount(mount_point).mount(container_id)
            if driver == 'devicemapper':
                DockerMount.mount_path(os.path.join(mount_point, "rootfs"), mount_point, bind=True)
            if cid:
                return DockerTemporaryMountPoint(driver, container_id, mount_point, cid)
            else:
                logger.error('Could not mount Container Id %s On %s' % (container_id, mount_point))
                shutil.rmtree(mount_point, ignore_errors=True)
                return None

    def _docker_inspect_image(docker_name, docker_type):
        a = json.loads(run_command_capture_output(
            "docker inspect --type %s %s" % (docker_type, docker_name)))
        if len(a) == 0:
            return None
        else:
            return a[0]

    def _docker_driver():
        x = "Storage Driver:"
        if UseAtomic:
            atomic_docker = "atomic"
        else:
            atomic_docker = "docker"
        for each in run_command_capture_output(atomic_docker + " info").splitlines():
            if each.startswith(x):
                return each[len(x):].strip()
        return ""

    def _docker_all_image_ids():
        l = []
        # why are we running docker images here and not atomic images?
        if UseAtomic:
            atomic_docker = "atomic images list"
        else:
            atomic_docker = "docker images"
        for each in run_command_capture_output(atomic_docker + " --quiet --no-trunc").splitlines():
            if each not in l:
                l.append(each)
        return l

    def _docker_all_container_ids():
        l = []
        if UseAtomic:
            atomic_docker = "atomic"
        else:
            atomic_docker = "docker"
        for each in run_command_capture_output(atomic_docker + " ps --all --quiet --no-trunc").splitlines():
            if each not in l:
                l.append(each)
        return l

else:
    # If we can't import docker or atomic then we stub out all the main functions to report errors
    if UseAtomic:
        the_verbiage = "Atomic"
        the_exception = HaveAtomicException
    else:
        the_verbiage = "Docker"
        the_exception = HaveDockerException

    def get_targets(config):
        logger.error('Could not connect to ' + the_verbiage + ' to collect from images and containers')
        logger.error(the_verbiage + ' is either not installed or not accessable: %s' %
                     (the_exception if the_exception else ''))
        return []

    def open_image(image_id):
        logger.error('Could not connect to ' + the_verbiage + ' to examine image %s' % image_id)
        logger.error(the_verbiage + ' is either not installed or not accessable: %s' %
                     (the_exception if the_exception else ''))
        return None

    def open_container(container_id):
        logger.error('Could not connect to ' + the_verbiage + ' to examine container %s' % container_id)
        logger.error(the_verbiage + ' is either not installed or not accessable: %s' %
                     (the_exception if the_exception else ''))
        return None
