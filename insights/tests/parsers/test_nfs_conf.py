from insights.parsers import nfs_conf as nfs_conf_parser
from insights.parsers.nfs_conf import NFSConf
from insights.tests import context_wrap
from doctest import testmod

NFS_CONF_1 = """
#
# This is a general configuration for the
# NFS daemons and tools
#
[general]
# pipefs-directory=/var/lib/nfs/rpc_pipefs
#
[exportfs]
# debug=0
#
[gssd]
# verbosity=0
# rpc-verbosity=0
# use-memcache=0
# use-machine-creds=1
use-gss-proxy=1
# avoid-dns=1
# limit-to-legacy-enctypes=0
# context-timeout=0
# rpc-timeout=5
# keytab-file=/etc/krb5.keytab
# cred-cache-directory=
# preferred-realm=
# set-home=1
# upcall-timeout=30
# cancel-timed-out-upcalls=0
#
[lockd]
# port=0
# udp-port=0
#
[mountd]
# debug=0
# manage-gids=n
# descriptors=0
# port=0
# threads=1
# reverse-lookup=n
# state-directory-path=/var/lib/nfs
# ha-callout=
# cache-use-ipaddr=n
# ttl=1800
#
[nfsdcld]
# debug=0
# storagedir=/var/lib/nfs/nfsdcld
#
[nfsdcltrack]
# debug=0
# storagedir=/var/lib/nfs/nfsdcltrack
#
[nfsd]
# debug=0
# threads=8
# host=
# port=0
# grace-time=90
# lease-time=90
# tcp=y
# vers2=n
vers3=n
# vers4=y
# vers4.0=y
# vers4.1=y
# vers4.2=y
rdma=y
rdma-port=20049
#
[statd]
# debug=0
# port=0
# outgoing-port=0
# name=
# state-directory-path=/var/lib/nfs/statd
# ha-callout=
# no-notify=0
#
[sm-notify]
# debug=0
# force=0
# retry-time=900
# outgoing-port=
# outgoing-addr=
# lift-grace=y
#
"""

NFS_CONF_2 = """
#
# This is a general configuration for the
# NFS daemons and tools
#
[general]
# pipefs-directory=/var/lib/nfs/rpc_pipefs
#
[exportfs]
# debug=0
#
[gssd]
# verbosity=0
# rpc-verbosity=0
# use-memcache=0
# use-machine-creds=1
# use-gss-proxy=1
# avoid-dns=1
# limit-to-legacy-enctypes=0
# context-timeout=0
"""

NFS_CONF_MODDOC = """
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
"""


def test_nfs_conf():
    conf = NFSConf(context_wrap(NFS_CONF_1))
    assert conf

    assert conf.get('gssd', 'use-gss-proxy') == '1'
    assert conf.get('nfsd', 'rdma') == 'y'


def test_nfs_exports_empty():
    conf = NFSConf(context_wrap(NFS_CONF_2))
    assert sorted(conf.sections()) == ['exportfs', 'general', 'gssd']


def test_module_documentation():
    failed, total = testmod(nfs_conf_parser, globs={
        "nfs_conf": NFSConf(context_wrap(NFS_CONF_MODDOC))
    })
    assert failed == 0
