import doctest
import pytest

from insights.core.exceptions import ContentException, ParseException, SkipComponent
from insights.parsers import azure_instance
from insights.parsers.azure_instance import AzureInstanceID, AzureInstancePlan, AzureInstanceType, AzurePublicIpv4Addresses
from insights.tests import context_wrap

# For AzureInstanceID
AZURE_ID = "f904ece8-c6c1-4b5c-881f-309b50f25e50"

# For AzureInstanceType
AZURE_TYPE_1 = "Standard_L32s"
AZURE_TYPE_2 = "Standard_NV48s_v3"
AZURE_TYPE_3 = """
 % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                  Dload  Upload   Total   Spent    Left  Speed
   0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
 100  1126  100  1126    0     0  1374k      0 --:--:-- --:--:-- --:--:-- 1099k
Standard_NV48s_v3
"""
AZURE_TYPE_DOC = "Standard_L64s_v2"
AZURE_TYPE_AB_1 = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()
AZURE_TYPE_AB_2 = """
curl: (7) couldn't connect to host
""".strip()
AZURE_TYPE_AB_3 = """
curl: (28) connect() timed out!
""".strip()
AZURE_TYPE_AB_4 = """
.micro
""".strip()
AZURE_TYPE_AB_5 = """
No module named insights.tools
""".strip()

# For AzureInstancePlan
AZURE_PLAN_1 = '{"name": "rhel7", "product": "rhel", "publisher": "Red Hat"}'
AZURE_PLAN_2 = '{"name": "", "product": "", "publisher": "Red Hat"}'
AZURE_PLAN_3 = '{"name": "", "product": "", "publisher": ""}'

AZURE_PLAN_4 = """
 % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                  Dload  Upload   Total   Spent    Left  Speed
   0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
 100  1126  100  1126    0     0  1374k      0 --:--:-- --:--:-- --:--:-- 1099k
{"name": "rhel7", "product": "rhel", "publisher": "Red Hat"}
"""

AZURE_PLAN_DOC = '{"name": "planName", "product": "planProduct", "publisher": "planPublisher"}'

AZURE_PLAN_AB_1 = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()
AZURE_PLAN_AB_2 = """
curl: (7) couldn't connect to host
""".strip()
AZURE_PLAN_AB_3 = """
curl: (28) connect() timed out!
""".strip()

# For AzurePublicIpv4Addresses and AzurePublicHostname
AZURE_LB_1 = """
{
  "loadbalancer": {
    "publicIpAddresses": [
      {
        "frontendIpAddress": "137.116.118.209",
        "privateIpAddress": "10.0.0.4"
      }
    ],
    "inboundRules": [],
    "outboundRules": []
  }
}
""".strip()

AZURE_LB_ERR1 = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()
AZURE_LB_ERR2 = """
curl: (7) couldn't connect to host
""".strip()
AZURE_LB_ERR3 = """
curl: (28) connect() timed out!
""".strip()
AZURE_LB_ERR4 = "}}}"


# Test AzureInstanceID
def test_azure_instance_id_ab_empty():
    with pytest.raises(SkipComponent):
        AzureInstanceID(context_wrap(''))


def test_azure_instance_id():
    azure = AzureInstanceID(context_wrap(AZURE_ID))
    assert azure.id == "f904ece8-c6c1-4b5c-881f-309b50f25e50"
    assert repr(azure) == "<instance_id: {0}>".format(azure.id)


# Test AzureInstanceType
def test_azure_instance_type_ab_other():
    with pytest.raises(SkipComponent):
        AzureInstanceType(context_wrap(AZURE_TYPE_AB_1))

    with pytest.raises(SkipComponent):
        AzureInstanceType(context_wrap(AZURE_TYPE_AB_2))

    with pytest.raises(SkipComponent):
        AzureInstanceType(context_wrap(AZURE_TYPE_AB_3))

    with pytest.raises(ParseException) as pe:
        AzureInstanceType(context_wrap(AZURE_TYPE_AB_4))
        assert 'Unrecognized type' in str(pe)

    with pytest.raises(ContentException) as pe:
        AzureInstanceType(context_wrap(AZURE_TYPE_AB_5))


def test_azure_instance_type_ab_empty():
    with pytest.raises(SkipComponent):
        AzureInstanceType(context_wrap(''))


def test_azure_instance_type():
    azure = AzureInstanceType(context_wrap(AZURE_TYPE_1))
    assert azure.type == "Standard"
    assert azure.size == "L32s"
    assert azure.version is None
    assert azure.raw == "Standard_L32s"
    assert repr(azure) == "<azure_type: {t}, size: {s}, version: {v},  raw: {r}>".format(
                t=azure.type, s=azure.size, v=azure.version, r=azure.raw)

    azure = AzureInstanceType(context_wrap(AZURE_TYPE_2))
    assert azure.type == "Standard"
    assert azure.size == "NV48s"
    assert azure.version == "v3"
    assert azure.raw == "Standard_NV48s_v3"
    assert "NV48s" in str(azure)


def test_azure_instance_type_stats():
    azure = AzureInstanceType(context_wrap(AZURE_TYPE_3))
    assert azure.type == "Standard"
    assert azure.size == "NV48s"
    assert azure.version == "v3"
    assert azure.raw == "Standard_NV48s_v3"


# Test AzureInstancePlan
def test_azure_instance_plan_ab_other():
    with pytest.raises(SkipComponent):
        AzureInstancePlan(context_wrap(AZURE_PLAN_AB_1))

    with pytest.raises(SkipComponent):
        AzureInstancePlan(context_wrap(AZURE_PLAN_AB_2))

    with pytest.raises(SkipComponent):
        AzureInstancePlan(context_wrap(AZURE_PLAN_AB_3))

    with pytest.raises(SkipComponent):
        AzureInstancePlan(context_wrap(''))

    with pytest.raises(ParseException):
        AzureInstancePlan(context_wrap(AZURE_PLAN_4))


def test_azure_instance_plan():
    azure = AzureInstancePlan(context_wrap(AZURE_PLAN_1))
    assert azure.name == "rhel7"
    assert azure.product == "rhel"
    assert azure.publisher == "Red Hat"
    assert azure.raw == '{"name": "rhel7", "product": "rhel", "publisher": "Red Hat"}'
    assert repr(azure) == "<azure_plan_name: {n}, product: {pr}, publisher: {pu}, raw: {r}".format(
            n=azure.name, pr=azure.product, pu=azure.publisher, r=azure.raw)

    azure = AzureInstancePlan(context_wrap(AZURE_PLAN_2))
    assert azure.name is None
    assert azure.product is None
    assert azure.publisher == "Red Hat"
    assert azure.raw == '{"name": "", "product": "", "publisher": "Red Hat"}'

    azure = AzureInstancePlan(context_wrap(AZURE_PLAN_3))
    assert azure.name is None
    assert azure.product is None
    assert azure.publisher is None
    assert azure.raw == '{"name": "", "product": "", "publisher": ""}'


def test_doc_examples():
    env = {
        'azure_id': AzureInstanceID(context_wrap(AZURE_ID)),
        'azure_plan': AzureInstancePlan(context_wrap(AZURE_PLAN_DOC)),
        'azure_type': AzureInstanceType(context_wrap(AZURE_TYPE_DOC)),
    }
    failed, total = doctest.testmod(azure_instance, globs=env)
    assert failed == 0


def test_azure_public_ipv4():
    with pytest.raises(SkipComponent):
        AzurePublicIpv4Addresses(context_wrap(AZURE_LB_ERR1))

    with pytest.raises(SkipComponent):
        AzurePublicIpv4Addresses(context_wrap(AZURE_LB_ERR2))

    with pytest.raises(SkipComponent):
        AzurePublicIpv4Addresses(context_wrap(AZURE_LB_ERR3))

    with pytest.raises(ParseException):
        AzurePublicIpv4Addresses(context_wrap(AZURE_LB_ERR4))

    azure = AzurePublicIpv4Addresses(context_wrap(AZURE_LB_1))
    assert azure[0] == "137.116.118.209"
