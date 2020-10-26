import pytest
import doctest
from insights.parsers import alibaba_instance_type
from insights.parsers.alibaba_instance_type import AlibabaInstanceType
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException

ALIBABA_TYPE_1 = "ecs.ebmg5s.24xlarge"
ALIBABA_TYPE_2 = "ecs.g6a.64xlarge"
ALIBABA_TYPE_3 = """
 % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                  Dload  Upload   Total   Spent    Left  Speed
   0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
 100  1126  100  1126    0     0  1374k      0 --:--:-- --:--:-- --:--:-- 1099k
ecs.c6a.16xlarge
"""
ALIBABA_TYPE_DOC = ALIBABA_TYPE_1
ALIBABA_TYPE_AB_1 = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()
ALIBABA_TYPE_AB_2 = """
curl: (7) couldn't connect to host
""".strip()
ALIBABA_TYPE_AB_3 = """
curl: (28) connect() timed out!
""".strip()
ALIBABA_TYPE_AB_4 = """
.micro
""".strip()


def test_alibaba_instance_type_ab_other():
    with pytest.raises(SkipException):
        AlibabaInstanceType(context_wrap(ALIBABA_TYPE_AB_1))

    with pytest.raises(SkipException):
        AlibabaInstanceType(context_wrap(ALIBABA_TYPE_AB_2))

    with pytest.raises(SkipException):
        AlibabaInstanceType(context_wrap(ALIBABA_TYPE_AB_3))

    with pytest.raises(ParseException) as pe:
        AlibabaInstanceType(context_wrap(ALIBABA_TYPE_AB_4))
        assert 'Unrecognized type' in str(pe)


def test_alibaba_instance_type_ab_empty():
    with pytest.raises(SkipException):
        AlibabaInstanceType(context_wrap(''))


def test_alibaba_instance_type():
    alibaba = AlibabaInstanceType(context_wrap(ALIBABA_TYPE_1))
    assert alibaba.type == "ebmg5s"
    assert alibaba.size == "24xlarge"
    assert alibaba.raw == ALIBABA_TYPE_1

    alibaba = AlibabaInstanceType(context_wrap(ALIBABA_TYPE_2))
    assert alibaba.type == "g6a"
    assert alibaba.size == "64xlarge"
    assert ALIBABA_TYPE_2 in str(alibaba)


def test_alibaba_instance_type_stats():
    alibaba = AlibabaInstanceType(context_wrap(ALIBABA_TYPE_3))
    assert alibaba.type == "c6a"
    assert alibaba.size == "16xlarge"
    assert alibaba.raw == "ecs.c6a.16xlarge"


def test_doc_examples():
    env = {
            'alibaba_inst': AlibabaInstanceType(context_wrap(ALIBABA_TYPE_DOC))
          }
    failed, total = doctest.testmod(alibaba_instance_type, globs=env)
    assert failed == 0
