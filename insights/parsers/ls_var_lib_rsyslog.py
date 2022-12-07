"""
LsVarLibRsyslog - command ``ls -lZ  /var/lib/rsyslog``
======================================================
"""


from insights.core import CommandParser, FileListing
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ls_var_lib_rsyslog)
class LsVarLibRsyslog(CommandParser, FileListing):
    """
    Parses output of ``ls -lZ  /var/lib/rsyslog`` command.

    Sample output::

        total 4
        -rw-------. 1 root root system_u:object_r:syslogd_var_lib_t:s0 127 Nov 30 03:40 imjournal.state

    Examples:
        >>> rsyslog_obj.dir_contains('/var/lib/rsyslog', 'imjournal.state')
        True
        >>> imjournal_entry = rsyslog_obj.dir_entry('/var/lib/rsyslog', 'imjournal.state')
        >>> imjournal_entry['se_type']
        'syslogd_var_lib_t'
    """
    pass
