from insights.tests import context_wrap
from insights.parsers.sysconfig import NfsSysconfig

SYSCONFIG_NFS = """
# Optional arguments passed to rpc.nfsd. See rpc.nfsd(8)
RPCNFSDARGS="--rdma=20049"
# Number of nfs server processes to be started.
# The default is 8.
#RPCNFSDCOUNT=16
#
# Set V4 grace period in seconds
#NFSD_V4_GRACE=90
#
# Set V4 lease period in seconds
#NFSD_V4_LEASE=90
#
# Optional arguments passed to rpc.mountd. See rpc.mountd(8)
RPCMOUNTDOPTS=""
# Port rpc.mountd should listen on.
#MOUNTD_PORT=892
#
# Optional arguments passed to rpc.statd. See rpc.statd(8)
STATDARG=""
# Port rpc.statd should listen on.
#STATD_PORT=662
# Outgoing port statd should used. The default is port
# is random
#STATD_OUTGOING_PORT=2020
# Specify callout program
#STATD_HA_CALLOUT="/usr/local/bin/foo"
#
#
# Optional arguments passed to sm-notify. See sm-notify(8)
SMNOTIFYARGS=""
#
# Optional arguments passed to rpc.idmapd. See rpc.idmapd(8)
RPCIDMAPDARGS=""
#
# Optional arguments passed to rpc.gssd. See rpc.gssd(8)
# Note: The rpc-gssd service will not start unless the
#       file /etc/krb5.keytab exists. If an alternate
#       keytab is needed, that separate keytab file
#       location may be defined in the rpc-gssd.service's
#       systemd unit file under the ConditionPathExists
#       parameter
RPCGSSDARGS=""
#
# Enable usage of gssproxy. See gssproxy-mech(8).
GSS_USE_PROXY="yes"
#
# Optional arguments passed to rpc.svcgssd. See rpc.svcgssd(8)
RPCSVCGSSDARGS=""
#
# Optional arguments passed to blkmapd. See blkmapd(8)
BLKMAPDARGS=""
RPCNFSDCOUNT=256
""".strip()


def test_sysconfig_nfs():
    result = NfsSysconfig(context_wrap(SYSCONFIG_NFS))
    assert result['GSS_USE_PROXY'] == 'yes'
    assert result['RPCNFSDARGS'] == '--rdma=20049'
    assert result.get('STATD_PORT') is None
