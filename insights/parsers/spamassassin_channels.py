"""
SpamassassinChannels - command ``/bin/grep -r '^\\s*CHANNELURL=' /etc/mail/spamassassin/channel.d``
=========================================================================================================
"""
import re
from collections import OrderedDict

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.spamassassin_channels)
class SpamassassinChannels(CommandParser):
    """
    Class for parsing the ``/bin/grep -r '^\\s*CHANNELURL=' /etc/mail/spamassassin/channel.d``
    command.

    Attributes:
        channels (OrderedDict): channels grouped by configuration file

    Sample output of this command is::

        /etc/mail/spamassassin/channel.d/sought.conf:CHANNELURL=sought.rules.yerp.org
        /etc/mail/spamassassin/channel.d/spamassassin-official.conf:CHANNELURL=updates.spamassassin.org

    Examples:
        >>> type(spamassassin_channels)
        <class 'insights.parsers.spamassassin_channels.SpamassassinChannels'>
        >>> spamassassin_channels.channels
        OrderedDict([('/etc/mail/spamassassin/channel.d/sought.conf', ['sought.rules.yerp.org']), ('/etc/mail/spamassassin/channel.d/spamassassin-official.conf', ['updates.spamassassin.org'])])
    """
    def __init__(self, *args, **kwargs):
        self.channels = OrderedDict()
        super(SpamassassinChannels, self).__init__(*args, **kwargs)

    def parse_content(self, content):

        for line in content:
            file_name, file_line = line.split(":", 1)
            channel = re.sub('^\\s*CHANNELURL=', '', file_line).strip()
            if file_name not in self.channels:
                self.channels[file_name] = []
            self.channels[file_name].append(channel)
