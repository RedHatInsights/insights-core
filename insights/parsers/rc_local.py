"""
RcLocal - file ``/etc/rc.d/rc.local``
=====================================
"""

from .. import Parser, parser, get_active_lines
from insights.specs import Specs


@parser(Specs.rc_local)
class RcLocal(Parser):
    """
    Parse the `/etc/rc.d/rc.local` file.

    Sample input::

        #!/bin/sh
        #
        # This script will be executed *after* all the other init scripts.
        # You can put your own initialization stuff in here if you don't
        # want to do the full Sys V style init stuff.

        touch /var/lock/subsys/local
        echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled

    Attributes
    ----------
    data: list
        List of all lines from `rc.local` that are not comments or blank

    Examples
    --------
    >>> shared[RcLocal].data[0]
    'touch /var/lock/subsys/local'
    >>> shared[RcLocal].get('kernel')
    ['echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled']

    """
    def parse_content(self, content):
        self.data = [l for l in get_active_lines(content)]

    def get(self, value):
        """Returns the lines containing string value."""
        return [l for l in self.data if value in l]
