import doctest
import pytest

from insights.core.exceptions import ParseException, SkipException
from insights.parsers import subscription_manager
from insights.parsers.subscription_manager import (SubscriptionManagerFacts,
                                                   SubscriptionManagerID)
from insights.tests import context_wrap

RHSM_FACTS_1 = """
aws_instance_id: 567890567890
network.ipv6_address: ::1
uname.sysname: Linux
uname.version: #1 SMP PREEMPT Fri Sep 2 16:07:40 EDT 2022
virt.host_type: rhev, kvm
virt.is_guest: True
""".strip()

RHSM_FACTS_NG_1 = """
XYC
Release not set
""".strip()

RHSM_ID_1 = """
system identity: 00000000-8f8c-4cb1-8023-111111111111
name: rhel7.localdomain
org name: 1234567
org ID: 1234567
""".strip()

RHSM_ID_NG_1 = """
name: rhel7.localdomain
org name: 1234567
org ID: 1234567
environment name: dev/x86_64
""".strip()

RHSM_ID_NG_2 = """
This system is not yet registered. Try 'subscription-manager register --help' for more information.
""".strip()


def test_subscription_manager_facts():
    ret = SubscriptionManagerFacts(context_wrap(RHSM_FACTS_1))
    for line in RHSM_FACTS_1.splitlines():
        key, value = line.split(': ', 1)
        assert ret[key] == value


def test_subscription_manager_facts_ng():
    with pytest.raises(ParseException):
        SubscriptionManagerFacts(context_wrap(RHSM_FACTS_NG_1))

    with pytest.raises(SkipException):
        SubscriptionManagerFacts(context_wrap(""))


def test_subscription_manager_id():
    ret = SubscriptionManagerID(context_wrap(RHSM_ID_1))
    assert ret.id == RHSM_ID_1.splitlines()[0].split(": ")[1]


def test_subscription_manager_id_ng():
    with pytest.raises(ParseException):
        SubscriptionManagerID(context_wrap(RHSM_ID_NG_1))

    with pytest.raises(ParseException):
        SubscriptionManagerID(context_wrap(RHSM_ID_NG_2))

    with pytest.raises(SkipException):
        SubscriptionManagerID(context_wrap(""))


def test_doc_examples():
    env = {
            'rhsm_id': SubscriptionManagerID(context_wrap(RHSM_ID_1)),
            'rhsm_facts': SubscriptionManagerFacts(context_wrap(RHSM_FACTS_1)),
          }
    failed, total = doctest.testmod(subscription_manager, globs=env)
    assert failed == 0
