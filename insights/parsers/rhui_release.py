"""
RHUI release commands or files
==============================

RHUISetRelease - command ``rhui_set_release``
---------------------------------------------
RHUIReleaseVer - file ``/etc/yum/vars/releasever`` or ``/etc/yum/vars/releasever``
----------------------------------------------------------------------------------
"""
import os

from insights.core import Parser, CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.rhui_releasever)
class RHUIReleaseVer(Parser):
    """
    Class for parsing the file `/etc/yum/vars/releasever` or `/etc/dnf/vars/releasever`.
    It will output the rhel minor release when a minor release is set,
    or emtpy when it isn't set. This file may not exist when there is no minor release
    is set.

    Sample input data::

        8.6

    Attributes:
        set (str): the set release.
        major (int): the major version of the set release.
        minor (int): the minor version of the set release.

    Raises:
       SkipComponent: When the content is not in expected format.

    Examples:
        >>> type(rhui_releasever)
        <class 'insights.parsers.rhui_release.RHUIReleaseVer'>
        >>> rhui_releasever.set
        '8.6'
        >>> rhui_releasever.major
        8
        >>> rhui_releasever.minor
        6
    """

    def parse_content(self, content):
        self.set = self.major = self.minor = None
        if len(content) == 0:
            # Release not set
            return
        if len(content) != 1:
            raise SkipComponent("Unexpected content: {0}".format(os.linesep.join(content)))
        rhel_version = content[0].strip()
        line_splits = rhel_version.split('.')
        if len(line_splits) == 2 and line_splits[0].isdigit() and line_splits[-1].isdigit():
            self.set = rhel_version
            self.major = int(line_splits[0])
            self.minor = int(line_splits[-1])
        elif rhel_version and rhel_version[0].isdigit():
            self.set = rhel_version
            self.major = int(rhel_version[0])
            # leave self.minor as None
        else:
            self.set = rhel_version


@parser(Specs.rhui_set_release)
class RHUISetRelease(CommandParser):
    """
    .. warning::
        This class is deprecated and will be removed from 3.6.0.
        Please use the :class:`insights.parsers.rhui_release.RHUIReleaseVer` instead.

    Class for parsing the output of `rhui_set_release` command.
    It will output the rhel minor release when a minor release is set,
    or emtpy when it isn't set.

    Typical output of the command is::

        8.6

    Attributes:
        set (str): the set release.
        major (int): the major version of the set release.
        minor (int): the minor version of the set release.

    Examples:
        >>> type(rhui_rel)
        <class 'insights.parsers.rhui_release.RHUISetRelease'>
        >>> rhui_rel.set
        '8.6'
        >>> rhui_rel.major
        8
        >>> rhui_rel.minor
        6
    """

    def __init__(self, context, extra_bad_lines=None):
        deprecated(RHUISetRelease, "Please use the :class:`insights.parsers.rhui_release.RHUIReleaseVer` instead.", "3.6.0")
        super(RHUISetRelease, self).__init__(context, extra_bad_lines)

    def parse_content(self, content):
        self.set = self.major = self.minor = None
        if len(content) == 0:
            # Release not set
            return
        if len(content) == 1:
            rhel_version = content[0].strip()
            line_splits = rhel_version.split('.')
            if len(line_splits) == 2 and line_splits[0].isdigit() and line_splits[-1].isdigit():
                self.set = rhel_version
                self.major = int(line_splits[0])
                self.minor = int(line_splits[-1])
                return
        raise SkipComponent("Unexpected content: {0}".format(os.linesep.join(content)))
