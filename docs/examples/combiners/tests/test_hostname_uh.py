from insights.combiners.hostname_uh import HostnameUH
from insights.parsers.hostname import Hostname
from insights.parsers.uname import Uname
from insights.tests import context_wrap

HOSTNAME = "hostone_h.example.com"
UNAME = "Linux hostone_u.example.com 3.10.0-693.21.1.el7.x86_64 #1 SMP Fri Feb 23 18:54:16 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux"


def test_hostname_uh():
    hostname = Hostname(context_wrap(HOSTNAME))
    uname = Uname(context_wrap(UNAME))

    hostname_uh = HostnameUH(hostname, None)
    assert hostname_uh.hostname == HOSTNAME

    hostname_uh = HostnameUH(None, uname)
    assert hostname_uh.hostname == "hostone_u.example.com"

    hostname_uh = HostnameUH(hostname, uname)
    assert hostname_uh.hostname == HOSTNAME
