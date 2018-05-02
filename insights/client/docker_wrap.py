from __future__ import absolute_import
# !/usr/bin/python

from . import util
import json


class docker_wrapper:

    def __init__(self):
        cmd = ['docker', '-v']
        r = util.subp(cmd)
        if r.return_code != 0:
            raise Exception('Unable to communicate with the docker server')

    def inspect(self, obj_id):
        # returns dict representation of "docker inspect ID"
        cmd = ['docker', 'inspect', obj_id]
        r = util.subp(cmd)
        if r.return_code != 0:
            raise Exception('Unable to inspect object: %s' % obj_id)
        return json.loads(r.stdout)

    def driver(self):
        # returns the storage driver docker is using
        cmd = ['docker', 'info']
        r = util.subp(cmd)
        if r.return_code != 0:
            raise Exception('Unable to get docker info')

        for line in r.stdout.strip().split('\n'):
            if line.startswith('Storage Driver'):
                pre, _, post = line.partition(':')
                return post.strip()
        raise Exception('Unable to get docker storage driver')

    def dm_pool(self):
        # ONLY FOR DEVICEMAPPER
        # returns the docker-pool docker is using
        cmd = ['docker', 'info']
        r = util.subp(cmd)
        if r.return_code != 0:
            raise Exception('Unable to get docker info')
        for line in r.stdout.strip().split('\n'):
            if line.strip().startswith('Pool Name'):
                pre, _, post = line.partition(':')
                return post.strip()
        raise Exception('Unable to get docker pool name')

    def images(self, allI=False, quiet=False):
        # returns a list of dicts, each dict is an image's information
        # except when quiet is used - which returns a list of image ids
        # dict keys:
            # Created
            # Labels
            # VirtualSize
            # ParentId
            # RepoTags
            # RepoDigests
            # Id
            # Size
        cmd = ['docker', 'images', '-q', '--no-trunc']
        if allI:
            cmd.append("-a")
        r = util.subp(cmd)
        if r.return_code != 0:
            raise Exception('Unable to get docker images')
        images = r.stdout.strip().split('\n')
        if quiet:
            return images
        else:
            ims = []
            for i in images:
                inspec = self.inspect(i)
                inspec = inspec[0]
                dic = {}
                dic['Created'] = inspec['Created']
                if inspec['Config']:
                    dic['Labels'] = inspec['Config']['Labels']
                else:
                    dic['Labels'] = {}
                dic['VirtualSize'] = inspec['VirtualSize']
                dic['ParentId'] = inspec['Parent']
                dic['RepoTags'] = inspec['RepoTags']
                dic['RepoDigests'] = inspec['RepoDigests']
                dic['Id'] = inspec['Id']
                dic['Size'] = inspec['Size']
                ims.append(dic)
            return ims

    def containers(self, allc=False, quiet=False):
        # returns a list of dicts, each dict is an containers's information
        # except when quiet is used - which returns a list of container ids
        # dict keys:
            # Status
            # Created
            # Image
            # Labels
            # NetworkSettings
            # HostConfig
            # ImageID
            # Command
            # Names
            # Id
            # Ports

        cmd = ['docker', 'ps', '-q']
        if allc:
            cmd.append("-a")
        r = util.subp(cmd)
        if r.return_code != 0:
            raise Exception('Unable to get docker containers')
        containers = r.stdout.strip().split('\n')
        if quiet:
            return containers
        else:
            conts = []
            for i in containers:
                inspec = self.inspect(i)
                inspec = inspec[0]
                dic = {}
                dic['Status'] = inspec['State']['Status']
                dic['Created'] = inspec['Created']
                dic['Image'] = inspec['Config']['Image']
                dic['Labels'] = inspec['Config']['Labels']
                dic['NetworkSettings'] = inspec['NetworkSettings']
                dic['HostConfig'] = inspec['HostConfig']
                dic['ImageID'] = inspec['Image']
                dic['Command'] = inspec['Config']['Cmd']
                dic['Names'] = inspec['Name']
                dic['Id'] = inspec['Id']
                dic['Ports'] = inspec['NetworkSettings']['Ports']
                conts.append(dic)
            return conts
