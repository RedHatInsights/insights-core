import unittest

from insights.mappers import docker_sysconfig
from insights.tests import context_wrap

docker_sysconfig1 = """
OPTIONS= #'--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'

DOCKER_CERT_PATH=/etc/docker  # skbfvkfdble

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'
"""

docker_sysconfig2 = """
OPTIONS='--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'

DOCKER_CERT_PATH=/etc/docker  # skbfvkfdble

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'
"""

docker_sysconfig3 = """
OPTIONS='--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'

DOCKER_CERT_PATH=

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'
"""

docker_sysconfig4 = """
OPTIONS='--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'

DOCKER_CERT_PATH

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'
"""

DOCKER_SYSCONFIG_STD = """
# /etc/sysconfig/docker

# Modify these options if you want to change the way the docker daemon runs
OPTIONS='--selinux-enabled'

DOCKER_CERT_PATH=/etc/docker

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'

# If you want to block registries from being used, uncomment the BLOCK_REGISTRY
# option and give it a set of registries, each prepended with --block-registry
# flag. For example adding docker.io will stop users from downloading images
# from docker.io
# BLOCK_REGISTRY='--block-registry'

# If you have a registry secured with https but do not have proper certs
# distributed, you can tell docker to not look for full authorization by
# adding the registry to the INSECURE_REGISTRY line and uncommenting it.
# INSECURE_REGISTRY='--insecure-registry'

# On an SELinux system, if you remove the --selinux-enabled option, you
# also need to turn on the docker_transition_unconfined boolean.
# setsebool -P docker_transition_unconfined 1

# Location used for temporary files, such as those created by
# docker load and build operations. Default is /var/lib/docker/tmp
# Can be overriden by setting the following environment variable.
# DOCKER_TMPDIR=/var/tmp

# Controls the /etc/cron.daily/docker-logrotate cron job status.
# To disable, uncomment the line below.
# LOGROTATE=false
"""


class Sysconfigdockercheck(unittest.TestCase):
    def test_OPTION(self):
        result = docker_sysconfig.docker_sysconfig_parser(context_wrap(docker_sysconfig1))
        expected = {"OPTIONS": "",
                    "ADD_REGISTRY": "--add-registry registry.access.redhat.com",
                    "DOCKER_CERT_PATH": "/etc/docker"}
        self.assertEqual(expected, result)

        result = docker_sysconfig.docker_sysconfig_parser(context_wrap(docker_sysconfig2))
        expected = {"OPTIONS": "--selinux-enabled --log-opt max-size=10m --log-opt max-file=7",
                    "ADD_REGISTRY": "--add-registry registry.access.redhat.com",
                    "DOCKER_CERT_PATH": "/etc/docker"}
        self.assertEqual(expected, result)

        result = docker_sysconfig.docker_sysconfig_parser(context_wrap(docker_sysconfig3))
        expected = {"OPTIONS": "--selinux-enabled --log-opt max-size=10m --log-opt max-file=7",
                    "ADD_REGISTRY": "--add-registry registry.access.redhat.com",
                    "DOCKER_CERT_PATH": ""}
        self.assertEqual(expected, result)

        result = docker_sysconfig.docker_sysconfig_parser(context_wrap(docker_sysconfig4))
        expected = {"OPTIONS": "--selinux-enabled --log-opt max-size=10m --log-opt max-file=7",
                    "ADD_REGISTRY": "--add-registry registry.access.redhat.com"}
        self.assertEqual(expected, result)

    def test_standard_content(self):
        context = context_wrap(DOCKER_SYSCONFIG_STD, 'etc/sysconfig/docker')
        sysconf = docker_sysconfig.DockerSysconfig(context)

        self.assertEqual(
            sorted(sysconf.data.keys()),
            sorted(['OPTIONS', 'DOCKER_CERT_PATH', 'ADD_REGISTRY'])
        )
        self.assertTrue('OPTIONS' in sysconf.data)
        self.assertEqual(sysconf.data['OPTIONS'], '--selinux-enabled')
        self.assertEqual(sysconf.options, '--selinux-enabled')
        self.assertTrue('DOCKER_CERT_PATH' in sysconf.data)
        self.assertEqual(sysconf.data['DOCKER_CERT_PATH'], '/etc/docker')
        self.assertTrue('ADD_REGISTRY' in sysconf.data)
        self.assertEqual(sysconf.data['ADD_REGISTRY'], '--add-registry registry.access.redhat.com')

        self.assertEqual(sysconf.unparsed_lines, [])
