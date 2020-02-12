import doctest
import pytest
from insights.parsers import firewall_config
from insights.parsers.firewall_config import FirewallDConf
from insights.tests import context_wrap
from insights.parsers import SkipException

FIREWALLD_CONFIG = """
# firewalld config file

# default zone
# The default zone used if an empty zone string is used.
# Default: public
DefaultZone=public

# Minimal mark
# Marks up to this minimum are free for use for example in the direct
# interface. If more free marks are needed, increase the minimum
# Default: 100
MinimalMark=100

# Clean up on exit
# If set to no or false the firewall configuration will not get cleaned up
# on exit or stop of firewalld
# Default: yes
CleanupOnExit=yes


""".strip()

FIREWALLD_CONFIG_2 = """
""".strip()


def test_docs():
    env = {
        'firewalld': FirewallDConf(context_wrap(FIREWALLD_CONFIG))
    }
    failed, total = doctest.testmod(firewall_config, globs=env)
    assert failed == 0


def test_empty_content():
    with pytest.raises(SkipException):
        FirewallDConf(context_wrap(FIREWALLD_CONFIG_2))
