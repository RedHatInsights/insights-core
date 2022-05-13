import pytest
import doctest

from insights.parsers import azure_instance_plan
from insights.parsers.azure_instance_plan import AzureInstancePlan
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException

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


def test_azure_instance_place_ab_other():
    with pytest.raises(SkipException):
        AzureInstancePlan(context_wrap(AZURE_PLAN_AB_1))

    with pytest.raises(SkipException):
        AzureInstancePlan(context_wrap(AZURE_PLAN_AB_2))

    with pytest.raises(SkipException):
        AzureInstancePlan(context_wrap(AZURE_PLAN_AB_3))

    with pytest.raises(SkipException):
        AzureInstancePlan(context_wrap(''))

    with pytest.raises(ParseException):
        AzureInstancePlan(context_wrap(AZURE_PLAN_4))


def test_azure_instance_plan():
    azure = AzureInstancePlan(context_wrap(AZURE_PLAN_1))
    assert azure.name == "rhel7"
    assert azure.product == "rhel"
    assert azure.publisher == "Red Hat"
    assert azure.raw == '{"name": "rhel7", "product": "rhel", "publisher": "Red Hat"}'

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
        'azure_plan': AzureInstancePlan(context_wrap(AZURE_PLAN_DOC))
    }
    failed, total = doctest.testmod(azure_instance_plan, globs=env)
    assert failed == 0
