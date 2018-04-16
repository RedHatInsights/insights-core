from insights.core.plugins import combiner
from insights.parsers.hostname import Hostname
from insights.parsers.uname import Uname


@combiner([Hostname, Uname])
class HostnameUH(object):

    def __init__(self, hostname, uname):
        if hostname:
            self.hostname = hostname.fqdn
        else:
            self.hostname = uname.nodename
