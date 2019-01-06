from rules import heartburn
from insights.specs import Specs
from insights.tests import InputData, archive_provider
from insights.core.plugins import make_response


LSOF_EXAMPLE = """
COMMAND     PID   TID      USER    FD  TYPE    DEVICE  SIZE/OFF       NODE    NAME
sshd       1304     0   example   mem   REG     253,2    255888   10130663    /usr/lib64/libssl3.so
""".strip()

NETSTAT_TEXT = """
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address               Foreign Address             State       User       Inode      PID/Program name    Timer
tcp        0      0 0.0.0.0:322                 0.0.0.0:*                   LISTEN      0          13044      23041/irrelevant    off (0.00/0/0)
tcp        0      0 127.0.0.1:22                0.0.0.0:*                   LISTEN      0          30419      21968/sshd          off (0.00/0/0)
Active UNIX domain sockets (servers and established)
Proto RefCnt Flags       Type       State         I-Node PID/Program name    Path
unix  2      [ ACC ]     STREAM     LISTENING     17911  4220/multipathd     /var/run/multipathd.sock
""".strip()

INSTALLED_RPMS = """
xz-libs-4.999.9-0.3.beta.20091007git.el6.x86_64             Thu 22 Aug 2013 03:59:09 PM HKT
openssl-static-1.0.1e-16.el6_5.1.x86_64                     Thu 22 Aug 2013 03:59:09 PM HKT
rootfiles-8.1-6.1.el6.noarch                                Thu 22 Aug 2013 04:01:12 PM HKT
""".strip()


@archive_provider(heartburn.heartburn)
def integration_test():
    input_data = InputData("test_one")
    input_data.add(Specs.lsof, LSOF_EXAMPLE)
    input_data.add(Specs.installed_rpms, INSTALLED_RPMS)
    input_data.add(Specs.netstat, NETSTAT_TEXT)

    expected = make_response("YOU_HAVE_HEARTBURN", listening_pids=[1304])

    yield input_data, expected
