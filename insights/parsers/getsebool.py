"""
getsebool - command ``/usr/sbin/getsebool -a``
==============================================

This parser returns the output of the ``getsebool``
command.

Sample ``getsebool -a`` output::

    webadm_manage_user_files --> off
    webadm_read_user_files --> off
    wine_mmap_zero_ignore --> off
    xdm_bind_vnc_tcp_port --> off
    ssh_keysign --> off

Examples:

    >>> "webadm_manage_user_files" in getsebool
    True
    >>> "tmpreaper_use_nfs" in getsebool
    False
    >>> getsebool['ssh_keysign']
    'off'
"""

from .. import parser, Parser, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.getsebool)
class Getsebool(LegacyItemAccess, Parser):
    """
    The output of "getsebool" command is like following:

        tmpreaper_use_nfs --> off
        tmpreaper_use_samba --> off

    So we can return the value like {"tmpreaper_use_nfs":"off", "tmpreaper_use_samba":"off"}
    """

    def parse_content(self, content):
        self.data = {}
        for line in content:
            key, value = line.split("-->")
            self.data[key.strip()] = value.strip()
