"""
DockerSysconfig - file ``/etc/sysconfig/docker``
================================================

This parser provides access to the ``/etc/sysconfig/docker`` configuration
file, using the standard ``SysconfigOptions`` parser class.  The 'OPTIONS'
variable is also provided in the ``options`` property as a convenience.

The ``docker_sysconfig_parser`` function is also supplied as a deprecated
way to access the dictionary from the DockerSysconfig parser.

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

from .. import parser, SysconfigOptions
from insights.util import deprecated


@parser("docker_sysconfig")
class DockerSysconfig(SysconfigOptions):
    """
    .. warning::
        Deprecated parser, please use
        :class:`insights.parsers.sysconfig.DockerSysconfig` instead.

    Parse the ``/etc/sysconfig/docker`` file.
    """
    def __init__(self, *args, **kwargs):
        deprecated(DockerSysconfig, "Use the `DockerSysconfig` parser in the `sysconfig` module")
        super(DockerSysconfig, self).__init__(*args, **kwargs)

    @property
    def options(self):
        """ Return the value of the 'OPTIONS' variable, or '' if not defined. """
        return self.data.get('OPTIONS', '')


@parser("docker_sysconfig")
def docker_sysconfig_parser(context):
    """
    .. warning::
        Deprecated parser, please use
        :class:`insights.parsers.sysconfig.DockerSysconfig` instead.

    """
    return DockerSysconfig(context).data
