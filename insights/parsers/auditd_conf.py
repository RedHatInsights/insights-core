"""
Audit Conf files parsers
========================

The auditd.conf file is a standard key = value file with hash comments.
Active settings are provided using the `get_active_settings_value` method or
by using the dictionary `contains` functionality.

The audispd.conf file has the same format and usage with auditd.conf.

.. note::
    For Red Hat Enterprise Linux 7 and older, auditd and audispd are separate
    processes.
    Starting with Red Hat Enterprise Linux 8 the functionality of audispd has
    been migrated to auditd.

AuditdConf - file ``/etc/audit/auditd.conf``
--------------------------------------------

AudispdConf - file ``/etc/audisp/audispd.conf``
-----------------------------------------------

Example:

    >>> conf = shared[AuditdConf]
    >>> conf.get_active_setting_value('log_group')
    'root'
    >>> 'log_file' in conf
    True
"""

from .. import Parser, parser, get_active_lines
from ..parsers import split_kv_pairs
from insights.specs import Specs


class AuditConfParser(Parser):
    """
    A parser for accessing plain "key=value" configuration files,
    eg: ``/etc/audit/auditd.conf``.
    """

    def __init__(self, *args, **kwargs):
        self.active_lines_unparsed = []
        self.active_settings = {}
        super(AuditConfParser, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Parser context content
        """
        self.active_lines_unparsed = get_active_lines(content)
        #  (man page specifies that a line must contain "=")
        self.active_settings = split_kv_pairs(content, use_partition=False)

    def get_active_setting_value(self, setting_name):
        """
        Access active setting value by setting name.

        Args:
            setting_name (string): Setting name
        """
        return self.active_settings[setting_name]


@parser(Specs.auditd_conf)
class AuditdConf(AuditConfParser):
    pass


@parser(Specs.audispd_conf)
class AudispdConf(AuditConfParser):
    pass
