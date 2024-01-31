"""
Subscription manager release commands
=====================================

Shared parser for parsing output of the ``subscription-manager release``
commands.

SubscriptionManagerReleaseShow - command ``subscription-manager release --show``
--------------------------------------------------------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.subscription_manager_release_show)
class SubscriptionManagerReleaseShow(CommandParser):
    """
    .. warning::
        This class is deprecated and will be removed from 3.6.0.
        Please use the :class:`insights.parsers.rhsm_releasever.RhsmReleaseVer` instead.

    Class for parsing the output of `subscription-manager release --show` command.

    Typical output of the command is::

        Release: 7.2

    Attributes:
        set (str): the set release.
        major (int): the major version of the set release.
        minor (int): the minor version of the set release.

    Examples:
        >>> type(rhsm_rel)
        <class 'insights.parsers.subscription_manager_release.SubscriptionManagerReleaseShow'>
        >>> rhsm_rel.set
        '7.2'
        >>> rhsm_rel.major
        7
        >>> rhsm_rel.minor
        2
    """

    def __init__(self, *args, **kwargs):
        deprecated(SubscriptionManagerReleaseShow, "Please use the :class:`insights.parsers.rhsm_releasever.RhsmReleaseVer` instead.", "3.6.0")
        super(SubscriptionManagerReleaseShow, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        self.set = self.major = self.minor = None
        l = len(content)
        if l != 1:
            raise SkipComponent("Content takes at most 1 line ({0} given).".format(l))
        line = content[0].strip()
        if line != 'Release not set':
            line_splits = line.split()
            # Release: 6.7 or Release 7Server
            if len(line_splits) == 2:
                rel = line_splits[-1]
                rel_splits = rel.split('.')
                # Release: 6.7
                if len(rel_splits) == 2:
                    if rel_splits[0].isdigit() and rel_splits[-1].isdigit():
                        self.set = rel
                        self.major = int(rel_splits[0])
                        self.minor = int(rel_splits[-1])
                        return
                # Release: 7Server
                elif rel.endswith('Server') and rel[0].isdigit():
                    self.set = rel
                    self.major = int(rel[0])
                    # leave self.minor as None
                    return
                # Release: 8
                elif rel[0].isdigit() and len(rel) == 1:
                    self.set = rel
                    self.major = int(rel[0])
                    # leave self.minor as None
                    return

            raise SkipComponent("Incorrect content: {0}".format(line))
        # Release not set
