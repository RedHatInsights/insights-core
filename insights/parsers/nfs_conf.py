"""
General configuration file for NFS daemons and tools - ``/etc/nfs.conf``
========================================================================

This file contains site-specific configuration for various NFS daemons and
other processes. In particular, this encourages consistent configuration
across different processes.

NFSCONF - file ``/etc/nfs.conf``
--------------------------------

"""

from insights.core.plugins import parser
from insights.core import IniConfigFile
from insights.specs import Specs


@parser(Specs.nfs_conf)
class NFSCONF(IniConfigFile):
    """
    Class parses the ``/etc/nfs.conf`` file using the ``IniConfigFile`` base
    parser.

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
