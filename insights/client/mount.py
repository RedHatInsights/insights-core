from __future__ import print_function
from __future__ import absolute_import
# Copyright (C) 2016 Red Hat, All rights reserved.
# AUTHORS: William Temple <wtemple@redhat.com>
#          Brent Baude    <bbaude@redhat.com>
# Augments for POC by:
#          Alex Collins   <alcollin@redhat.com>

import os
import sys
import json

from .constants import InsightsConstants as constants

try:
    import docker
except ImportError:
    print("The docker-py Python libraries do not appear to be installed. Please install the python-docker-py RPM package.")
    sys.exit(constants.sig_kill_bad)
from fnmatch import fnmatch as matches

from . import util
from . import dmsetupWrap
from docker.utils import kwargs_from_env


""" Module for mounting and unmounting containerized applications. """


class MountError(Exception):

    """Generic error mounting a candidate container."""

    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)


class SelectionMatchError(MountError):

    """Input identifier matched multiple mount candidates."""

    def __init__(self, i, matches):
        self.val = ('"{0}" matched multiple items. Try one of the following:\n'
                    '{1}'.format(i, '\n'.join(['\t' + m for m in matches])))


class Mount:

    """
    A class which contains backend-independent methods useful for mounting and
    unmounting containers.
    """

    def __init__(self, mountpoint):
        """
        Constructs the Mount class with a mountpoint.
        Optional: mount a running container live (read/write)
        """
        self.mountpoint = mountpoint

    def mount(self, identifier, options=[]):
        raise NotImplementedError('Mount subclass does not implement mount() '
                                  'method.')

    def unmount(self):
        raise NotImplementedError('Mount subclass does not implement unmount()'
                                  ' method.')

    # LVM DeviceMapper Utility Methods
    @staticmethod
    def _activate_thin_device(name, dm_id, size, pool):
        """
        Provisions an LVM device-mapper thin device reflecting,
        DM device id 'dm_id' in the docker pool.
        """
        table = '0 %d thin /dev/mapper/%s %s' % (int(size) // 512, pool, dm_id)
        cmd = ['dmsetup', 'create', name, '--table', table]
        r = util.subp(cmd)
        if r.return_code != 0:
            raise MountError('Failed to create thin device: %s' %
                             r.stderr.decode(sys.getdefaultencoding()))

    @staticmethod
    def remove_thin_device(name, force=False):
        """
        Destroys a thin device via subprocess call.
        """
        cmd = ['dmsetup', 'remove', '--retry', name]
        r = util.subp(cmd)
        if not force:
            if r.return_code != 0:
                raise MountError('Could not remove thin device:\n%s' %
                                 r.stderr.decode(sys.getdefaultencoding()).split("\n")[0])

    @staticmethod
    def _is_device_active(device):
        """
        Checks dmsetup to see if a device is already active
        """
        cmd = ['dmsetup', 'info', device]
        dmsetup_info = util.subp(cmd)
        for dm_line in dmsetup_info.stdout.split("\n"):
            line = dm_line.split(':')
            if ('State' in line[0].strip()) and ('ACTIVE' in line[1].strip()):
                return True
        return False

    @staticmethod
    def _get_fs(thin_pathname):
        """
        Returns the file system type (xfs, ext4) of a given device
        """
        cmd = ['lsblk', '-o', 'FSTYPE', '-n', thin_pathname]
        fs_return = util.subp(cmd)
        return fs_return.stdout.strip()

    @staticmethod
    def mount_path(source, target, bind=False):
        """
        Subprocess call to mount dev at path.
        """
        cmd = ['mount']
        if bind:
            cmd.append('--bind')
        cmd.append(source)
        cmd.append(target)
        r = util.subp(cmd)
        if r.return_code != 0:
            raise MountError('Could not mount docker container:\n' +
                             ' '.join(cmd) + '\n%s' %
                             r.stderr.decode(sys.getdefaultencoding()))

    @staticmethod
    def get_dev_at_mountpoint(mntpoint):
        """
        Retrieves the device mounted at mntpoint, or raises
        MountError if none.
        """
        results = util.subp(['findmnt', '-o', 'SOURCE', mntpoint])
        if results.return_code != 0:
            raise MountError('No device mounted at %s' % mntpoint)

        stdout = results.stdout.decode(sys.getdefaultencoding())
        return stdout.replace('SOURCE\n', '').strip().split('\n')[-1]

    @staticmethod
    def unmount_path(path, force=False):
        """
        Unmounts the directory specified by path.
        """
        r = util.subp(['umount', path])
        if not force:
            if r.return_code != 0:
                raise ValueError(r.stderr)


class DockerMount(Mount):

    """
    A class which can be used to mount and unmount docker containers and
    images on a filesystem location.

    mnt_mkdir = Create temporary directories based on the cid at mountpoint
                for mounting containers
    """

    def __init__(self, mountpoint, mnt_mkdir=False):
        Mount.__init__(self, mountpoint)
        self.client = docker.Client(**kwargs_from_env())
        self.mnt_mkdir = mnt_mkdir
        self.tmp_image = None

    def _create_temp_container(self, iid):
        """
        Create a temporary container from a given iid.

        Temporary containers are marked with a sentinel environment
        variable so that they can be cleaned on unmount.
        """
        try:
            return self.client.create_container(
                image=iid, command='/bin/true',
                environment=['_ATOMIC_TEMP_CONTAINER'],
                detach=True, network_disabled=True)['Id']
        except docker.errors.APIError as ex:
            raise MountError('Error creating temporary container:\n%s' % str(ex))

    def _clone(self, cid):
        """
        Create a temporary image snapshot from a given cid.

        Temporary image snapshots are marked with a sentinel label
        so that they can be cleaned on unmount.
        """
        try:
            iid = self.client.commit(
                container=cid,
                conf={
                    'Labels': {
                        'io.projectatomic.Temporary': 'true'
                    }
                }
            )['Id']
        except docker.errors.APIError as ex:
            raise MountError(str(ex))
        self.tmp_image = iid
        return self._create_temp_container(iid)

    def _is_container_running(self, cid):
        cinfo = self.client.inspect_container(cid)
        return cinfo['State']['Running']

    def _identifier_as_cid(self, identifier):
        """
        Returns a container uuid for identifier.

        If identifier is an image UUID or image tag, create a temporary
        container and return its uuid.
        """
        def __cname_matches(container, identifier):
            return any([n for n in (container['Names'] or [])
                        if matches(n, '/' + identifier)])

        # Determine if identifier is a container
        containers = [c['Id'] for c in self.client.containers(all=True)
                      if (__cname_matches(c, identifier) or
                          matches(c['Id'], identifier + '*'))]

        if len(containers) > 1:
            raise SelectionMatchError(identifier, containers)
        elif len(containers) == 1:
            c = containers[0]
            return self._clone(c)

        # Determine if identifier is an image UUID
        images = [i for i in set(self.client.images(all=True, quiet=True))
                  if i.startswith(identifier)]

        if len(images) > 1:
            raise SelectionMatchError(identifier, images)
        elif len(images) == 1:
            return self._create_temp_container(images[0])

        # Match image tag.
        images = util.image_by_name(identifier)
        if len(images) > 1:
            tags = [t for i in images for t in i['RepoTags']]
            raise SelectionMatchError(identifier, tags)
        elif len(images) == 1:
            return self._create_temp_container(images[0]['Id'].replace("sha256:", ""))

        raise MountError('{} did not match any image or container.'
                         ''.format(identifier))

    @staticmethod
    def _no_gd_api_dm(cid):
        # TODO: Deprecated
        desc_file = os.path.join('/var/lib/docker/devicemapper/metadata', cid)
        desc = json.loads(open(desc_file).read())
        return desc['device_id'], desc['size']

    @staticmethod
    def _no_gd_api_overlay(cid):
        # TODO: Deprecated
        prefix = os.path.join('/var/lib/docker/overlay/', cid)
        ld_metafile = open(os.path.join(prefix, 'lower-id'))
        ld_loc = os.path.join('/var/lib/docker/overlay/', ld_metafile.read())
        return (os.path.join(ld_loc, 'root'), os.path.join(prefix, 'upper'),
                os.path.join(prefix, 'work'))

    def mount(self, identifier):
        """
        Mounts a container or image referred to by identifier to
        the host filesystem.
        """

        driver = self.client.info()['Driver']
        driver_mount_fn = getattr(self, "_mount_" + driver,
                                  self._unsupported_backend)
        cid = driver_mount_fn(identifier)

        # Return mount path so it can be later unmounted by path
        return self.mountpoint, cid

    def _unsupported_backend(self, identifier=''):
        raise MountError('Insights cannot be used with the {} docker '
                         'storage backend.'
                         ''.format(self.client.info()['Driver']))

    def _mount_devicemapper(self, identifier):
        """
        Devicemapper mount backend.
        """

        info = self.client.info()

        # cid is the contaienr_id of the temp container
        cid = self._identifier_as_cid(identifier)

        cinfo = self.client.inspect_container(cid)

        dm_dev_name, dm_dev_id, dm_dev_size = '', '', ''
        dm_pool = info['DriverStatus'][0][1]

        try:
            dm_dev_name = cinfo['GraphDriver']['Data']['DeviceName']
            dm_dev_id = cinfo['GraphDriver']['Data']['DeviceId']
            dm_dev_size = cinfo['GraphDriver']['Data']['DeviceSize']
        except:
            # TODO: deprecated when GraphDriver patch makes it upstream
            dm_dev_id, dm_dev_size = DockerMount._no_gd_api_dm(cid)
            dm_dev_name = dm_pool.replace('pool', cid)

        # grab list of devces
        dmsetupLs = dmsetupWrap.getDmsetupLs()
        if dmsetupLs == -1:
            raise MountError('Error: dmsetup returned non zero error ')

        # ENSURE device exists!
        if dm_dev_name not in dmsetupLs:
            # IF device doesn't exist yet we create it!
            Mount._activate_thin_device(dm_dev_name, dm_dev_id, dm_dev_size,
                                        dm_pool)

        # check that device is shown in /dev/mapper, if not we can use the
        # major minor numbers in /dev/block
        mapperDir = os.path.join('/dev/mapper', dm_dev_name)
        if os.path.exists(mapperDir):
            dm_dev_path = mapperDir
        else:
            # get new dmsetupLs after device has been created!
            dmsetupLs = dmsetupWrap.getDmsetupLs()
            # test if device exists in dmsetupls, if so, get its majorminor found in /dev/block
            majorMinor = dmsetupWrap.getMajorMinor(dm_dev_name, dmsetupLs)
            blockDir = os.path.join('/dev/block', majorMinor)

            # FIXME, coudl be due to Virtual box, but occasionally the block device
            # will not be created by the time we check it exists below, so we
            # can wait a half a second to let it be created up
            import time
            time.sleep(0.1)

            if os.path.exists(blockDir):
                dm_dev_path = blockDir
            else:
                raise MountError('Error: Block device found in dmsetup ls '
                                 'but not in /dev/mapper/ or /dev/block')

        options = ['ro', 'nosuid', 'nodev']
        # XFS should get nouuid
        fstype = Mount._get_fs(dm_dev_path).decode(sys.getdefaultencoding())
        if fstype.upper() == 'XFS' and 'nouuid' not in options:
            if 'nouuid' not in options:
                options.append('nouuid')
        try:
            Mount.mount_path(dm_dev_path, self.mountpoint)
        except MountError as de:
            self._cleanup_container(cinfo)
            Mount.remove_thin_device(dm_dev_name)
            raise de

        # return the temp container ID so we can unmount later
        return cid

    def _mount_overlay(self, identifier):
        """
        OverlayFS mount backend.
        """

        cid = self._identifier_as_cid(identifier)
        cinfo = self.client.inspect_container(cid)

        ld, ud, wd = '', '', ''
        try:
            ld = cinfo['GraphDriver']['Data']['lowerDir']
            ud = cinfo['GraphDriver']['Data']['upperDir']
            wd = cinfo['GraphDriver']['Data']['workDir']
        except:
            ld, ud, wd = DockerMount._no_gd_api_overlay(cid)

        options = ['ro', 'lowerdir=' + ld, 'upperdir=' + ud, 'workdir=' + wd]
        optstring = ','.join(options)
        cmd = ['mount', '-t', 'overlay', '-o', optstring, 'overlay',
               self.mountpoint]
        status = util.subp(cmd)
        if status.return_code != 0:
            self._cleanup_container(cinfo)
            raise MountError('Failed to mount OverlayFS device.\n%s' %
                             status.stderr.decode(sys.getdefaultencoding()))

        return cid

    def _cleanup_container(self, cinfo):
        """
        Remove a container and clean up its image if necessary.
        """
        # I'm not a fan of doing this again here.
        env = cinfo['Config']['Env']
        if (env and '_ATOMIC_TEMP_CONTAINER' not in env) or not env:
            return

        iid = cinfo['Image']
        self.client.remove_container(cinfo['Id'])
        try:
            labels = self.client.inspect_image(iid)['Config']['Labels']
        except TypeError:
            labels = {}
        if labels and 'io.projectatomic.Temporary' in labels:
            if labels['io.projectatomic.Temporary'] == 'true':
                self.client.remove_image(iid)

    def _clean_tmp_image(self):
        # If a temporary image is created with commit,
        # clean up that too
        if self.tmp_image is not None:
            self.client.remove_image(self.tmp_image, noprune=True)

    def unmount(self, cid):
        """
        Unmounts and cleans-up after a previous mount().
        """
        driver = self.client.info()['Driver']
        driver_unmount_fn = getattr(self, "_unmount_" + driver,
                                    self._unsupported_backend)
        driver_unmount_fn(cid)

    def _unmount_devicemapper(self, cid):
        """
        Devicemapper unmount backend.
        """
        mountpoint = self.mountpoint
        Mount.unmount_path(mountpoint)

        cinfo = self.client.inspect_container(cid)
        dev_name = cinfo['GraphDriver']['Data']['DeviceName']

        Mount.remove_thin_device(dev_name)
        self._cleanup_container(cinfo)

    def _unmount_overlay(self, cid):
        """
        OverlayFS unmount backend.
        """
        mountpoint = self.mountpoint
        Mount.unmount_path(mountpoint)
        self._cleanup_container(self.client.inspect_container(cid))

    def _clean_temp_container_by_path(self, path):
        short_cid = os.path.basename(path)
        self.client.remove_container(short_cid)
        self._clean_tmp_image()
