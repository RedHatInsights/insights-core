import doctest
import pytest

from insights.combiners import cloud_instance
from insights.combiners.cloud_provider import CloudProvider
from insights.combiners.cloud_instance import CloudInstance
from insights.core.exceptions import ContentException, SkipComponent
from insights.parsers.aws_instance_id import AWSInstanceIdDoc
from insights.parsers.azure_instance import AzureInstanceID, AzureInstanceType
from insights.parsers.dmidecode import DMIDecode
from insights.parsers.cloud_init import CloudInitQuery
from insights.parsers.gcp_instance_type import GCPInstanceType
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.subscription_manager import SubscriptionManagerFacts
from insights.tests import context_wrap
from insights.tests.combiners.test_cloud_provider import RPMS_AWS, RPMS_GOOGLE
from insights.tests.parsers.test_aws_instance_id import AWS_ID_DOC
from insights.tests.parsers.test_azure_instance import AZURE_ID_1, AZURE_TYPE_2
from insights.tests.parsers.test_cloud_init import CLOUD_INIT_QUERY_OUTPUT1 as CLOUD_QUERY_AZURE
from insights.tests.parsers.test_gcp_instance_type import GOOGLE_TYPE_1
from insights.tests.parsers.test_subscription_manager import FACTS_NORMAL_1

GOOGLE_RHSM_FACTS = """
gcp_instance_id: 567890567890
network.ipv6_address: ::1
uname.sysname: Linux
""".strip()

AWS_RHSM_FACTS = """
aws_instance_id: i-01234567890abcdef
aws_instance_type: m5.large
""".strip()

AWS_RHSM_FACTS_NO_TYPE = """
aws_instance_id: i-01234567890abcdef
""".strip()

AWS_DMIDECODE = """
# dmidecode 3.3
Getting SMBIOS data from sysfs.
SMBIOS 2.7 present.
13 structures occupying 568 bytes.
Table at 0xBFFF0000.

Handle 0x0000, DMI type 0, 24 bytes
BIOS Information
    Vendor: Amazon EC2
    Version: 1.0
    Release Date: 10/16/2017
    Address: 0xF0000
    Runtime Size: 64 kB
    ROM Size: 64 kB
    Characteristics:
        PCI is supported
        EDD is supported
        ACPI is supported
        System is a virtual machine
    BIOS Revision: 1.0

Handle 0x000C, DMI type 127, 4 bytes
End Of Table
""".strip()


def test_cloud_instance_google():
    rpms = InstalledRpms(context_wrap(RPMS_GOOGLE))
    _type = GCPInstanceType(context_wrap(GOOGLE_TYPE_1))
    cp = CloudProvider(rpms, None, None, None, None, None)
    facts = SubscriptionManagerFacts(context_wrap(GOOGLE_RHSM_FACTS))
    ret = CloudInstance(cp, None, None, None, _type, facts)
    assert ret.provider == CloudProvider.GOOGLE
    assert ret.id == "567890567890"
    assert ret.type == "n2-highcpu-16"
    assert ret.size == "n2-highcpu-16"


def test_cloud_instance_aws():
    rpms = InstalledRpms(context_wrap(RPMS_AWS))
    _id = AWSInstanceIdDoc(context_wrap(AWS_ID_DOC))
    cp = CloudProvider(rpms, None, None, None, None, None)
    ret = CloudInstance(cp, _id, None, None, None, None)
    assert ret.provider == CloudProvider.AWS
    assert ret.id == "i-1234567890abcdef0"
    assert ret.type == "t2.micro"
    assert ret.size == "t2.micro"


def test_cloud_instance_azure():
    cloud_query = CloudInitQuery(context_wrap(CLOUD_QUERY_AZURE))
    _id = AzureInstanceID(context_wrap(AZURE_ID_1))
    _type = AzureInstanceType(context_wrap(AZURE_TYPE_2))
    cp = CloudProvider(None, None, None, None, cloud_query, None)
    ret = CloudInstance(cp, None, _id, _type, None, None)
    assert ret.provider == CloudProvider.AZURE
    assert ret.id == "f904ece8-c6c1-4b5c-881f-309b50f25e50"
    assert ret.type == "Standard_NV48s_v3"
    assert ret.size == "Standard_NV48s_v3"


def test_cloud_instance_aws_from_submanfacts():
    rpms = InstalledRpms(context_wrap(RPMS_AWS))
    bios = DMIDecode(context_wrap(AWS_DMIDECODE))
    facts = SubscriptionManagerFacts(context_wrap(AWS_RHSM_FACTS))
    cp = CloudProvider(rpms, bios, None, None, None, facts)
    ret = CloudInstance(cp, None, None, None, None, facts)
    assert ret.provider == CloudProvider.AWS
    assert ret.id == "i-01234567890abcdef"
    assert ret.type == "m5.large"
    assert ret.size == "m5.large"


def test_cloud_instance_aws_from_submanfacts_no_type():
    rpms = InstalledRpms(context_wrap(RPMS_AWS))
    bios = DMIDecode(context_wrap(AWS_DMIDECODE))
    facts = SubscriptionManagerFacts(context_wrap(AWS_RHSM_FACTS_NO_TYPE))
    cp = CloudProvider(rpms, bios, None, None, None, facts)
    ret = CloudInstance(cp, None, None, None, None, facts)
    assert ret.provider == CloudProvider.AWS
    assert ret.id == "i-01234567890abcdef"
    assert ret.type is None
    assert ret.size is None


def test_cloud_instance_ex():
    rpms = InstalledRpms(context_wrap(RPMS_GOOGLE))
    _type = GCPInstanceType(context_wrap(GOOGLE_TYPE_1))
    cp = CloudProvider(rpms, None, None, None, None, None)
    aws_facts = SubscriptionManagerFacts(context_wrap(FACTS_NORMAL_1))

    with pytest.raises(ContentException) as ce:
        CloudInstance(cp, None, None, None, None, aws_facts)
    assert "Unmatched" in str(ce)

    with pytest.raises(SkipComponent):
        CloudInstance(cp, None, None, None, _type, None)


def test_cloud_instance_doc():
    rpms = InstalledRpms(context_wrap(RPMS_AWS))
    _id = AWSInstanceIdDoc(context_wrap(AWS_ID_DOC))
    cp = CloudProvider(rpms, None, None, None, None, None)
    env = {'ci': CloudInstance(cp, _id, None, None, None, None)}
    failed, total = doctest.testmod(cloud_instance, globs=env)
    assert failed == 0
