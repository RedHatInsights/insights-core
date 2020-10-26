import pytest
import doctest
from insights.parsers import google_instance_type
from insights.parsers.google_instance_type import GoogleInstanceType
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException
from insights.core.plugins import ContentException

GOOGLE_TYPE_1 = "projects/123456789/machineTypes/n2-highcpu-16"
GOOGLE_TYPE_2 = "projects/123456789/machineTypes/e2-medium"
GOOGLE_TYPE_3 = """
 % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                  Dload  Upload   Total   Spent    Left  Speed
   0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
 100  1126  100  1126    0     0  1374k      0 --:--:-- --:--:-- --:--:-- 1099k
projects/123456789/machineTypes/e2-medium
"""
GOOGLE_TYPE_DOC = GOOGLE_TYPE_1
GOOGLE_TYPE_AB_1 = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()
GOOGLE_TYPE_AB_2 = """
curl: (7) couldn't connect to host
""".strip()
GOOGLE_TYPE_AB_3 = """
curl: (28) connect() timed out!
""".strip()
GOOGLE_TYPE_AB_4 = """
.micro
""".strip()


def test_google_instance_type_ab_other():
    with pytest.raises(SkipException):
        GoogleInstanceType(context_wrap(GOOGLE_TYPE_AB_1))

    with pytest.raises(SkipException):
        GoogleInstanceType(context_wrap(GOOGLE_TYPE_AB_2))

    with pytest.raises(SkipException):
        GoogleInstanceType(context_wrap(GOOGLE_TYPE_AB_3))

    with pytest.raises(ParseException) as pe:
        GoogleInstanceType(context_wrap(GOOGLE_TYPE_AB_4))
        assert 'Unrecognized type' in str(pe)


def test_google_instance_type_ab_empty():
    with pytest.raises(SkipException):
        GoogleInstanceType(context_wrap(''))


def test_google_instance_type():
    google = GoogleInstanceType(context_wrap(GOOGLE_TYPE_1))
    assert google.type == "n2"
    assert google.size == "highcpu-16"
    assert google.raw == "n2-highcpu-16"
    assert google.raw_line == GOOGLE_TYPE_1

    google = GoogleInstanceType(context_wrap(GOOGLE_TYPE_2))
    assert google.type == "e2"
    assert google.size == "medium"
    assert google.raw == "e2-medium"
    assert google.raw_line == GOOGLE_TYPE_2
    assert "e2-medium" in str(google)


def test_google_instance_type_stats():
    google = GoogleInstanceType(context_wrap(GOOGLE_TYPE_3))
    assert google.type == "e2"
    assert google.size == "medium"
    assert google.raw == "e2-medium"
    assert google.raw_line == GOOGLE_TYPE_2
    assert "e2-medium" in str(google)


def test_doc_examples():
    env = {
            'google_inst': GoogleInstanceType(context_wrap(GOOGLE_TYPE_DOC))
          }
    failed, total = doctest.testmod(google_instance_type, globs=env)
    assert failed == 0
