"""
LsVarLibRsyslog - command ``ls -lZ  /var/lib/rsyslog``
======================================================
"""


from insights.core import CommandParser, FileListing
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.ls_var_lib_rsyslog)
class LsVarLibRsyslog(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSlanZ` instead.

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
    def __init__(self, *args, **kwargs):
        deprecated(LsVarLibRsyslog, "Please use the :class:`insights.parsers.ls.LSlanZ` instead.", "3.5.0")
        super(LsVarLibRsyslog, self).__init__(*args, **kwargs)
