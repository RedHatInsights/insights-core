import doctest
import pytest

from insights.combiners import cloud_instance
from insights.combiners.cloud_provider import CloudProvider
from insights.combiners.cloud_instance import CloudInstance
from insights.core.exceptions import ContentException, SkipComponent
from insights.parsers.aws_instance_id import AWSInstanceIdDoc
from insights.parsers.azure_instance import AzureInstanceID, AzureInstanceType
from insights.parsers.gcp_instance_type import GCPInstanceType
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.subscription_manager import SubscriptionManagerFacts
from insights.tests import context_wrap
from insights.tests.combiners.test_cloud_provider import RPMS_AWS, RPMS_GOOGLE, RPMS_AZURE
from insights.tests.parsers.test_aws_instance_id import AWS_ID_DOC
from insights.tests.parsers.test_azure_instance import AZURE_ID, AZURE_TYPE_2
from insights.tests.parsers.test_gcp_instance_type import GOOGLE_TYPE_1
from insights.tests.parsers.test_subscription_manager import FACTS_NORMAL_1

GOOGLE_RHSM_FACTS = """
gcp_instance_id: 567890567890
network.ipv6_address: ::1
uname.sysname: Linux
""".strip()


def test_cloud_instance_google():
    rpms = InstalledRpms(context_wrap(RPMS_GOOGLE))
    _type = GCPInstanceType(context_wrap(GOOGLE_TYPE_1))
    cp = CloudProvider(rpms, None, None, None)
    facts = SubscriptionManagerFacts(context_wrap(GOOGLE_RHSM_FACTS))
    ret = CloudInstance(cp, None, None, None, _type, facts)
    assert ret.provider == CloudProvider.GOOGLE
    assert ret.id == "567890567890"
    assert ret.type == "n2-highcpu-16"
    assert ret.size == "n2-highcpu-16"


def test_cloud_instance_aws():
    rpms = InstalledRpms(context_wrap(RPMS_AWS))
    _id = AWSInstanceIdDoc(context_wrap(AWS_ID_DOC))
    cp = CloudProvider(rpms, None, None, None)
    ret = CloudInstance(cp, _id, None, None, None, None)
    assert ret.provider == CloudProvider.AWS
    assert ret.id == "i-1234567890abcdef0"
    assert ret.type == "t2.micro"
    assert ret.size == "t2.micro"


def test_cloud_instance_azure():
    rpms = InstalledRpms(context_wrap(RPMS_AZURE))
    _id = AzureInstanceID(context_wrap(AZURE_ID))
    _type = AzureInstanceType(context_wrap(AZURE_TYPE_2))
    cp = CloudProvider(rpms, None, None, None)
    ret = CloudInstance(cp, None, _id, _type, None, None)
    assert ret.provider == CloudProvider.AZURE
    assert ret.id == "f904ece8-c6c1-4b5c-881f-309b50f25e50"
    assert ret.type == "Standard_NV48s_v3"
    assert ret.size == "Standard_NV48s_v3"


def test_cloud_instance_ex():
    rpms = InstalledRpms(context_wrap(RPMS_GOOGLE))
    _type = GCPInstanceType(context_wrap(GOOGLE_TYPE_1))
    cp = CloudProvider(rpms, None, None, None)
    aws_facts = SubscriptionManagerFacts(context_wrap(FACTS_NORMAL_1))

    with pytest.raises(ContentException) as ce:
        CloudInstance(cp, None, None, None, None, aws_facts)
    assert "Unmatched" in str(ce)

    with pytest.raises(SkipComponent):
        CloudInstance(cp, None, None, None, _type, None)


def test_cloud_instance_doc():
    rpms = InstalledRpms(context_wrap(RPMS_AWS))
    _id = AWSInstanceIdDoc(context_wrap(AWS_ID_DOC))
    cp = CloudProvider(rpms, None, None, None)
    env = {'ci': CloudInstance(cp, _id, None, None, None, None)}
    failed, total = doctest.testmod(cloud_instance, globs=env)
    assert failed == 0
