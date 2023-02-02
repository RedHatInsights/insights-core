import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import subscription_manager
from insights.parsers.subscription_manager import SubscriptionManagerFacts
from insights.tests import context_wrap

INPUT_NORMAL_1 = """
aws_instance_id: 567890567890
network.ipv6_address: ::1
uname.sysname: Linux
uname.version: #1 SMP PREEMPT Fri Sep 2 16:07:40 EDT 2022
virt.host_type: rhev, kvm
virt.is_guest: True
""".strip()

INPUT_NG_1 = """
XYC
Release not set
""".strip()

INPUT_NG_2 = ""


def test_subscription_manager_facts():
    ret = SubscriptionManagerFacts(context_wrap(INPUT_NORMAL_1))
    for line in INPUT_NORMAL_1.splitlines():
        key, value = line.split(': ', 1)
        assert ret[key] == value


def test_subscription_manager_release_show_ng():
    with pytest.raises(ParseException):
        SubscriptionManagerFacts(context_wrap(INPUT_NG_1))

    with pytest.raises(SkipComponent):
        SubscriptionManagerFacts(context_wrap(INPUT_NG_2))


def test_doc_examples():
    env = {
            'rhsm_facts':
            SubscriptionManagerFacts(context_wrap(INPUT_NORMAL_1)),
          }
    failed, total = doctest.testmod(subscription_manager, globs=env)
    assert failed == 0
