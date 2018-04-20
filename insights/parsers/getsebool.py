"""
getsebool - command ``/usr/sbin/getsebool -a``
===================================================

This parser returns the output of the ``getsebool``
command.

Example getsebool output:

    webadm_manage_user_files --> off
    webadm_read_user_files --> off
    wine_mmap_zero_ignore --> off
    xdm_bind_vnc_tcp_port --> off
    ssh_keysign --> off

Examples:

    >>> sebool = Getsebool(context_wrap(getseboolvalue))
    >>> sebool['ssh_keysign']
    'off'
"""

from .. import parser, Parser
from insights.specs import Specs


@parser(Specs.getsebool)
class Getsebool(Parser):
    """
    The output of "getsebool" command is like following:
        tmpreaper_use_nfs --> off
        tmpreaper_use_samba --> off
    So we can return the value like {"tmpreaper_use_nfs":"off", "tmpreaper_use_samba":"off"}
    """

    def parse_content(self, content):
        self._data = {}
        for line in content:
            key, value = line.split("-->")
            self._data[key.strip()] = value.strip()

    def __contains__(self, boolkey):
        """
        Check if the bool exists in the output
        """
        return boolkey in self._data

    def __getitem__(self, boolkey):
        """
        Return the request with the given bool key.
        """
        return self._data[boolkey]
