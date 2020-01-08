import doctest
from insights.parsers import udev_rules
from insights.parsers.udev_rules import UdevRules
from insights.tests import context_wrap

UDEV_RULES_FILT_HIT = """
ENV{FC_TARGET_WWPN}!="$*"; GOTO="fc_wwpn_end"
ENV{FC_INITIATOR_WWPN}!="$*"; GOTO="fc_wwpn_end"
ENV{FC_TARGET_LUN}!="$*"; GOTO="fc_wwpn_end"
""".strip()


def test_documentation():
    env = {'udev_rules': UdevRules(context_wrap(UDEV_RULES_FILT_HIT))}
    failed_count, tests = doctest.testmod(udev_rules, globs=env)
    assert failed_count == 0


def test_udev_rules():
    result = UdevRules(context_wrap(UDEV_RULES_FILT_HIT))
    for line in ['ENV{FC_TARGET_WWPN}!="$*"; GOTO="fc_wwpn_end"',
                 'ENV{FC_INITIATOR_WWPN}!="$*"; GOTO="fc_wwpn_end"',
                  'ENV{FC_TARGET_LUN}!="$*"; GOTO="fc_wwpn_end"']:
        assert line in result.lines
