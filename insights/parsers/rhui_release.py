"""
RHUI release commands
=====================

RHUISetRelease - command ``rhui_set_release``
---------------------------------------------

"""
import os

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


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
