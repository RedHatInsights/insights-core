import unittest

from falafel.mappers import docker_sysconfig
from falafel.tests import context_wrap

docker_sysconfig1="""
OPTIONS=#'--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'

DOCKER_CERT_PATH=/etc/docker  # skbfvkfdble

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'
"""

docker_sysconfig2="""
OPTIONS='--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'

DOCKER_CERT_PATH=/etc/docker  # skbfvkfdble

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'
"""

docker_sysconfig3="""
OPTIONS='--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'

DOCKER_CERT_PATH=

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'
"""

docker_sysconfig4="""
OPTIONS='--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'

DOCKER_CERT_PATH

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'
"""

class Sysconfigdockercheck(unittest.TestCase):
    def test_OPTION(self):
        result = docker_sysconfig.docker_sysconfig_parser(context_wrap(docker_sysconfig1))
        expected = {"OPTIONS": "", "ADD_REGISTRY": "'--add-registry registry.access.redhat.com'",
                    "DOCKER_CERT_PATH": "/etc/docker"}
        self.assertEqual(expected, result)

        result = docker_sysconfig.docker_sysconfig_parser(context_wrap(docker_sysconfig2))
        expected = {"OPTIONS": "'--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'",
                    "ADD_REGISTRY": "'--add-registry registry.access.redhat.com'", "DOCKER_CERT_PATH": "/etc/docker"}
        self.assertEqual(expected, result)

        result = docker_sysconfig.docker_sysconfig_parser(context_wrap(docker_sysconfig3))
        expected = {"OPTIONS": "'--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'",
                    "ADD_REGISTRY": "'--add-registry registry.access.redhat.com'", "DOCKER_CERT_PATH": ""}
        self.assertEqual(expected, result)

        result = docker_sysconfig.docker_sysconfig_parser(context_wrap(docker_sysconfig4))
        expected = {"OPTIONS": "'--selinux-enabled --log-opt max-size=10m --log-opt max-file=7'",
                    "ADD_REGISTRY": "'--add-registry registry.access.redhat.com'"}
        self.assertEqual(expected, result)

