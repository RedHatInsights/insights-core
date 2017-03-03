from falafel.mappers.openshift_certificates import OpenShiftCertificates
from falafel.tests import context_wrap
import datetime

CRT1 = """
notAfter=Nov 24 02:58:22 2021 GMT
""".strip()

CRT1_PATH = "etc/origin/master/ca.crt"

CRT2 = """
notAfter=Nov 25 03:02:04 2018 GMT
""".strip()

CRT2_PATH = "etc/origin/node/server.crt"


def test_openshift_certficates():
    Cert = OpenShiftCertificates(context_wrap(CRT1, path=CRT1_PATH))
    assert Cert.file_name == 'ca.crt'
    assert Cert.GetExpirationDate() == datetime.datetime(2021, 11, 24, 2, 58, 22)

    Cert2 = OpenShiftCertificates(context_wrap(CRT2, path=CRT2_PATH))
    assert Cert2.file_name == 'server.crt'
    assert Cert2.GetExpirationDate() == datetime.datetime(2018, 11, 25, 3, 2, 4)
