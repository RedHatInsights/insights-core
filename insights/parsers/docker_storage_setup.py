"""
DockerStorageSetup - file ``/etc/sysconfig/docker-storage-setup``
=================================================================

A fairly simple parser to read the contents of the docker storage setup
configuration.

Sample input::

    # Edit this file to override any configuration options specified in
    # /usr/lib/docker-storage-setup/docker-storage-setup.
    #
    # For more details refer to "man docker-storage-setup"
    VG=vgtest
    AUTO_EXTEND_POOL=yes
    ##name = mydomain
    POOL_AUTOEXTEND_THRESHOLD=60
    POOL_AUTOEXTEND_PERCENT=20

Examples:

    >>> setup = shared[DockerStorageSetup]
    >>> setup['VG'] # Pseudo-dict access
    'vgtest'
    >>> 'name' in setup
    False
    >>> setup.data['POOL_AUTOEXTEND_THRESHOLD'] # old style access
    '60'

"""

from insights.util import deprecated
from .. import SysconfigOptions, parser
from insights.specs import Specs


@parser(Specs.docker_storage_setup)
class DockerStorageSetup(SysconfigOptions):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.sysconfig.DockerStorageSetupSysconfig` instead.

    A parser for accessing /etc/sysconfig/docker-storage-setup.
    """
    def __init__(self, *args, **kwargs):
        deprecated(DockerStorageSetup, "Import DockerStorageSetupSysconfig from insights.parsers.sysconfig instead")
        super(DockerStorageSetup, self).__init__(*args, **kwargs)
