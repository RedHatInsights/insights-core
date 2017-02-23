"""
DockerSysconfig - file ``/etc/sysconfig/docker``
================================================

This mapper provides access to the ``/etc/sysconfig/docker`` configuration
file, using the standard ``SysconfigOptions`` mapper class.  The 'OPTIONS'
variable is also provided in the ``options`` property as a convenience.

The ``docker_sysconfig_parser`` function is also supplied as a deprecated
way to access the dictionary from the DockerSysconfig mapper.

Sample input::

    # /etc/sysconfig/docker

    # Modify these options if you want to change the way the docker daemon runs
    OPTIONS='--selinux-enabled'

    DOCKER_CERT_PATH=/etc/docker

    # If you want to add your own registry to be used for docker search and docker
    # pull use the ADD_REGISTRY option to list a set of registries, each prepended
    # with --add-registry flag. The first registry added will be the first registry
    # searched.
    ADD_REGISTRY='--add-registry registry.access.redhat.com'

Examples:

    >>> conf = shared[DockerSysconfig]
    >>> 'OPTIONS' in conf
    True
    >>> conf.data['OPTIONS']
    '--selinux-enabled'
    >>> conf.options
    '--selinux-enabled'
    >>> conf.data['DOCKER_CERT_PATH']
    '/etc/docker'

"""

from .. import mapper, SysconfigOptions


@mapper("docker_sysconfig")
class DockerSysconfig(SysconfigOptions):
    """
    Parse the ``/etc/sysconfig/docker`` file.
    """
    pass

    @property
    def options(self):
        """ Return the value of the 'OPTIONS' variable, or '' if not defined. """
        return self.data.get('OPTIONS', '')


@mapper("docker_sysconfig")
def docker_sysconfig_parser(context):
    """
    Deprecated - please use the ``DockerSysconfig`` mapper class.
    """
    return DockerSysconfig(context).data
