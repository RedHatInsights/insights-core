import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import subscription_manager
from insights.parsers.subscription_manager import SubscriptionManagerID, SubscriptionManagerFacts, SubscriptionManagerStatus
from insights.tests import context_wrap

FACTS_NORMAL_1 = """
aws_instance_id: 567890567890
network.ipv6_address: ::1
uname.sysname: Linux
uname.version: #1 SMP PREEMPT Fri Sep 2 16:07:40 EDT 2022
virt.host_type: rhev, kvm
virt.is_guest: True
""".strip()

FACTS_with_AB_LINES = """
You are attempting to use a locale that is not installed.
aws_instance_id: 567890567890
network.ipv6_address: ::1
uname.sysname: Linux
uname.version: #1 SMP PREEMPT Fri Sep 2 16:07:40 EDT 2022
virt.host_type: rhev, kvm
virt.is_guest: True
""".strip()

ID_NORMAL_1 = """
system identity: 6655c27c-f561-4c99-a23f-f53e5a1ef311
name: rhel7.localdomain
org name: 1234567
org ID: 1234567
""".strip()

ID_with_AB_LINES = """
You are attempting to use a locale that is not installed.
system identity: 6655c27c-f561-4c99-a23f-f53e5a1ef311
name: rhel7.localdomain
org name: 1234567
org ID: 1234567
""".strip()

INPUT_NG_1 = """
XYC
Release not set
""".strip()

INPUT_NG_2 = ""


SUBSCRIPTION_MANAGER_STATUS = """
+-------------------------------------------+
   System Status Details
+-------------------------------------------+
Overall Status: Disabled
Content Access Mode is set to Simple Content Access. This host has access to content, regardless of subscription status.

System Purpose Status: Disabled
""".strip()

SUBSCRIPTION_MANAGER_STATUS_EMPTY = """

""".strip()

SUBSCRIPTION_MANAGER_STATUS_PRODUCT_KEY = """
+-------------------------------------------+
   System Status Details
+-------------------------------------------+
Overall Status: Insufficient

Red Hat Enterprise Linux for Virtual Datacenters, Standard:
- Guest has not been reported on any host and is using a temporary unmapped guest subscription. For more information, please see https://access.redhat.com/solutions/XXXX

System Purpose Status: Matched
""".strip()


def test_subman_facts():
    ret = SubscriptionManagerFacts(context_wrap(FACTS_NORMAL_1))
    for line in FACTS_NORMAL_1.splitlines():
        key, value = line.split(': ', 1)
        assert ret[key] == value

    ret = SubscriptionManagerFacts(context_wrap(FACTS_with_AB_LINES))
    for line in FACTS_NORMAL_1.splitlines():
        if ': ' not in line:
            continue
        key, value = line.split(': ', 1)
        assert ret[key] == value


def test_subman_id():
    ret = SubscriptionManagerID(context_wrap(ID_NORMAL_1))
    for line in ID_NORMAL_1.splitlines():
        key, value = line.split(': ', 1)
        assert ret[key] == value
    assert ret.identity == '6655c27c-f561-4c99-a23f-f53e5a1ef311'

    ret = SubscriptionManagerID(context_wrap(ID_with_AB_LINES))
    for line in ID_with_AB_LINES.splitlines():
        if ': ' not in line:
            continue
        key, value = line.split(': ', 1)
        assert ret[key] == value
    assert ret.identity == '6655c27c-f561-4c99-a23f-f53e5a1ef311'


def test_subman_status():
    ret = SubscriptionManagerStatus(context_wrap(SUBSCRIPTION_MANAGER_STATUS))
    assert ret['Overall Status'] == 'Disabled'
    assert ret['Content Access Mode'] == 'Simple Content Access'
    assert ret['System Purpose Status'] == 'Disabled'

    ret = SubscriptionManagerStatus(context_wrap(SUBSCRIPTION_MANAGER_STATUS_PRODUCT_KEY))
    assert ret['Overall Status'] == 'Insufficient'
    assert ret['Red Hat Enterprise Linux for Virtual Datacenters'] == 'Standard'
    assert ret['System Purpose Status'] == 'Matched'
    assert ret.unparsed_lines == [SUBSCRIPTION_MANAGER_STATUS_PRODUCT_KEY.splitlines()[-3]]


def test_subman_facts_ng():
    with pytest.raises(SkipComponent):
        SubscriptionManagerFacts(context_wrap(INPUT_NG_1))

    with pytest.raises(SkipComponent):
        SubscriptionManagerFacts(context_wrap(INPUT_NG_2))


def test_subman_id_ng():
    with pytest.raises(SkipComponent):
        SubscriptionManagerID(context_wrap(INPUT_NG_1))

    with pytest.raises(SkipComponent):
        SubscriptionManagerID(context_wrap(INPUT_NG_2))


def test_subman_status_ng():
    with pytest.raises(SkipComponent):
        SubscriptionManagerStatus(context_wrap(SUBSCRIPTION_MANAGER_STATUS_EMPTY))


def test_doc_examples():
    env = {
            'rhsm_facts': SubscriptionManagerFacts(context_wrap(FACTS_with_AB_LINES)),
            'subman_id': SubscriptionManagerID(context_wrap(ID_with_AB_LINES)),
            'subman_status': SubscriptionManagerStatus(context_wrap(SUBSCRIPTION_MANAGER_STATUS)),
          }
    failed, total = doctest.testmod(subscription_manager, globs=env)
    assert failed == 0
