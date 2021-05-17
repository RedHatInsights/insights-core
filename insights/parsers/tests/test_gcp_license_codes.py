import pytest
import doctest

from insights.parsers import gcp_license_codes
from insights.parsers.gcp_license_codes import GCPLicenseCodes
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException

GCP_LICENSE_CODES_1 = '[{"id": "123451234512345"}]'
GCP_LICENSE_CODES_2 = '[{"id": "123451234512345"}, {"id": "238949287234"}]'
GCP_LICENSE_CODES_3 = '[]'

GCP_LICENSE_CODES_4 = """
 % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                  Dload  Upload   Total   Spent    Left  Speed
   0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
 100  1126  100  1126    0     0  1374k      0 --:--:-- --:--:-- --:--:-- 1099k
[{"id": "123451234512345"}]
"""

GCP_LICENSE_CODES_DOC = '[{"id": "601259152637613565"}]'

GCP_LICENSE_CODES_AB_1 = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()
GCP_LICENSE_CODES_AB_2 = """
curl: (7) couldn't connect to host
""".strip()
GCP_LICENSE_CODES_AB_3 = """
curl: (28) connect() timed out!
""".strip()


def test_azure_instance_place_ab_other():
    with pytest.raises(SkipException):
        GCPLicenseCodes(context_wrap(GCP_LICENSE_CODES_AB_1))

    with pytest.raises(SkipException):
        GCPLicenseCodes(context_wrap(GCP_LICENSE_CODES_AB_2))

    with pytest.raises(SkipException):
        GCPLicenseCodes(context_wrap(GCP_LICENSE_CODES_AB_3))

    with pytest.raises(SkipException):
        GCPLicenseCodes(context_wrap(''))

    with pytest.raises(ParseException):
        GCPLicenseCodes(context_wrap(GCP_LICENSE_CODES_4))


def test_gcp_license_codes():
    gcp_licenses = GCPLicenseCodes(context_wrap(GCP_LICENSE_CODES_1))
    assert gcp_licenses.ids == ["123451234512345"]
    assert gcp_licenses.raw == [{"id": "123451234512345"}]

    gcp_licenses = GCPLicenseCodes(context_wrap(GCP_LICENSE_CODES_2))
    assert gcp_licenses.ids == ["123451234512345", "238949287234"]
    assert gcp_licenses.raw == [{"id": "123451234512345"}, {"id": "238949287234"}]

    gcp_licenses = GCPLicenseCodes(context_wrap(GCP_LICENSE_CODES_3))
    assert gcp_licenses.ids is None
    assert gcp_licenses.raw == []


def test_doc_examples():
    env = {
        'gcp_licenses': GCPLicenseCodes(context_wrap(GCP_LICENSE_CODES_DOC))
    }
    failed, total = doctest.testmod(gcp_license_codes, globs=env)
    assert failed == 0
