import doctest
import pytest

from insights.parsers import spamassassin_channels
from insights.parsers.spamassassin_channels import SpamassassinChannels
from insights.tests import context_wrap

DEFAULT = """
/etc/mail/spamassassin/channel.d/sought.conf:CHANNELURL=sought.rules.yerp.org
/etc/mail/spamassassin/channel.d/spamassassin-official.conf:CHANNELURL=updates.spamassassin.org
""".strip()

SPACES = """
/etc/mail/spamassassin/channel.d/sought.conf:  CHANNELURL=sought.rules.yerp.org
/etc/mail/spamassassin/channel.d/spamassassin-official.conf:CHANNELURL=updates.spamassassin.org
""".strip()

TWO_IN_FILE = """
/etc/mail/spamassassin/channel.d/sought.conf:CHANNELURL=sought.rules.yerp.org
/etc/mail/spamassassin/channel.d/sought.conf:CHANNELURL=sought2.rules.yerp.org
/etc/mail/spamassassin/channel.d/spamassassin-official.conf:CHANNELURL=updates.spamassassin.org
""".strip()


TEST_CASES = [
    (DEFAULT, {
        "/etc/mail/spamassassin/channel.d/sought.conf": ["sought.rules.yerp.org"],
        "/etc/mail/spamassassin/channel.d/spamassassin-official.conf": ["updates.spamassassin.org"],
               }
     ),
    (SPACES, {
        "/etc/mail/spamassassin/channel.d/sought.conf": ["sought.rules.yerp.org"],
        "/etc/mail/spamassassin/channel.d/spamassassin-official.conf": ["updates.spamassassin.org"],
               }
     ),
    (TWO_IN_FILE, {
        "/etc/mail/spamassassin/channel.d/sought.conf": ["sought.rules.yerp.org", "sought2.rules.yerp.org"],
        "/etc/mail/spamassassin/channel.d/spamassassin-official.conf": ["updates.spamassassin.org"],
               }
     ),
]


@pytest.mark.parametrize("input, output", TEST_CASES)
def test_spamassassin_channels(input, output):
    test = SpamassassinChannels(context_wrap(input))
    assert test.channels == output


def test_doc_examples():
    env = {
        "spamassassin_channels": SpamassassinChannels(context_wrap(DEFAULT)),
    }
    failed, total = doctest.testmod(spamassassin_channels, globs=env)
    assert failed == 0
