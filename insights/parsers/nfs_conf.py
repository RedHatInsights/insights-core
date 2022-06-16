"""
General configuration file for NFS daemons and tools - ``/etc/nfs.conf``
========================================================================

This file contains site-specific configuration for various NFS daemons and
other processes. In particular, this encourages consistent configuration
across different processes.

NFSConf - file ``/etc/nfs.conf``
--------------------------------

"""

from insights.core.plugins import parser
from insights.core import IniConfigFile
from insights.specs import Specs


@parser(Specs.nfs_conf)
class NFSConf(IniConfigFile):
    """
    Class parses the ``/etc/nfs.conf`` file using the ``IniConfigFile`` base
    parser.

    .. note::
        In some RHEL version, both the file ``/etc/nfs.conf`` and file
        ``/etc/sysconfig/nfs`` exist, and take effect at the same time for NFS
        services on the host. And it's possible that there are overlaps between
        the two configuration files.
        A combiner for the two configuration files was considered.
        Since the two files' coverage are different, and it is quite complicate
        to enumerate all the configuration options and combine them properly,
        and also, ``/etc/sysconfig/nfs`` is deprecated in lately RHEL releases.
        We deselect it as a consequence.

    Sample configuration file::

        [general]
        # pipefs-directory=/var/lib/nfs/rpc_pipefs

        [exportfs]
        debug=0

        [gssd]
        use-gss-proxy=1

        [nfsd]
        # debug=0
        vers3=n
        # vers4=y
        # vers4.0=y
        # vers4.1=y
        # vers4.2=y
        rdma=y
        rdma-port=20049

    Examples:
        >>> sorted(nfs_conf.sections())
        ['exportfs', 'general', 'gssd', 'nfsd']
        >>> nfs_conf.get('gssd', 'use-gss-proxy')
        '1'
        >>> nfs_conf.getint('gssd', 'use-gss-proxy')
        1
        >>> nfs_conf.get('nfsd', 'vers3')
        'n'
        >>> nfs_conf.get('nfsd', 'rdma-port')
        '20049'
    """
    pass
