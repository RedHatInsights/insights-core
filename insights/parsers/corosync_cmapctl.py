"""
CorosyncCmapctl - Command ``corosync-cmapctl [params]``
=======================================================

This module parses the output of the ``corosync-cmapctl [params]`` command.
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.corosync_cmapctl)
class CorosyncCmapctl(CommandParser, dict):
    """
    Class for parsing the `/usr/sbin/corosync-cmapctl [params]` command.
    All lines are stored in the dictionary with the left part of the equal
    sign witout parenthese info as the key and the right part of equal sign
    as the value.

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
        SkipComponent: When there is no content
        ParseException: When there is no "=" in the content
    """

    def __init__(self, context):
        super(CorosyncCmapctl, self).__init__(context, extra_bad_lines=['corosync-cmapctl: invalid option'])

    def parse_content(self, content):
        if not content:
            raise SkipComponent
        for line in content:
            if '=' not in line:
                raise ParseException("Can not parse line %s" % line)
            key, value = [item.strip() for item in line.split('=')]
            key_without_parenthese = key.split()[0]
            self[key_without_parenthese] = value
