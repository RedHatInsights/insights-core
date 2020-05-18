"""
CorosyncCmapctl - Command ``corosync-cmapctl [params]``
=======================================================

This module parses the output of the ``corosync-cmapctl [params]`` command.
"""

from insights import parser, CommandParser, LegacyItemAccess
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.corosync_cmapctl)
class CorosyncCmapctl(CommandParser, LegacyItemAccess):
    """
    Class for parsing the `/usr/sbin/corosync-cmapctl [params]` command.

    Typical output of the command is::

        config.totemconfig_reload_in_progress (u8) = 0
        internal_configuration.service.0.name (str) = corosync_cmap
        internal_configuration.service.0.ver (u32) = 0
        internal_configuration.service.1.name (str) = corosync_cfg
        internal_configuration.service.1.ver (u32) = 0
        internal_configuration.service.2.name (str) = corosync_cpg
        internal_configuration.service.2.ver (u32) = 0

    Examples:
        >>> type(corosync)
        <class 'insights.parsers.corosync_cmapctl.CorosyncCmapctl'>
        >>> 'internal_configuration.service.0.name' in corosync
        True
        >>> corosync['internal_configuration.service.0.name']
        'corosync_cmap'

    Raises:
        SkipException: When there is no content
        ParseException: When there is no "=" in the content

    Attributes:
        data (dict): All lines are stored in this dictionary with the left
                     part of the equal sign witout parenthese info as the
                     key and the right part of equal sign as the value
        stats_schedmiss (dict): The lines which start with
                                "stats.schedmiss" are stored in this
                                dictionary. The key and value format is
                                the same with data
    """

    def __init__(self, context):
        super(CorosyncCmapctl, self).__init__(context, extra_bad_lines=['corosync-cmapctl: invalid option'])

    def parse_content(self, content):
        if not content:
            raise SkipException
        self.data = {}
        self.stats_schedmiss = {}
        for line in content:
            if '=' not in line:
                raise ParseException("Can not parse line %s" % line)
            key, value = [item.strip() for item in line.split('=')]
            key_without_parenthese = key.split()[0]
            if key_without_parenthese.startswith('stats.schedmiss'):
                self.stats_schedmiss[key_without_parenthese] = value
            self.data[key_without_parenthese] = value
