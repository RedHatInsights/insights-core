import unittest
from datetime import datetime
from insights.mappers.certificates_enddate import CertificatesEnddate
from insights.tests import context_wrap


CRT1 = """
/usr/bin/find: '/etc/origin/node': No such file or directory
/usr/bin/find: '/etc/origin/master': No such file or directory
notAfter=May 25 16:39:40 2019 GMT
FileName= /etc/origin/node/cert.pem
unable to load certificate
139881193203616:error:0906D066:PEM routines:PEM_read_bio:bad end line:pem_lib.c:802:
unable to load certificate
140695459370912:error:0906D06C:PEM routines:PEM_read_bio:no start line:pem_lib.c:703:Expecting: TRUSTED CERTIFICATE
notAfter=May 25 16:39:40 2019 GMT
FileName= /etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem
notAfter=Dec  9 10:55:38 2017 GMT
FileName= /etc/pki/consumer/cert.pem
notAfter=Jan  1 04:59:59 2022 GMT
FileName= /etc/pki/entitlement/3343502840335059594.pem
notAfter=Aug 31 02:19:59 2017 GMT
FileName= /etc/pki/consumer/cert.pem
notAfter=Jan  1 04:59:59 2022 GMT
FileName= /etc/pki/entitlement/2387590574974617178.pem
""".strip()

CRT2 = ""

CRT3 = """
FileName= /etc/origin/node/cert.pem
notAfter=May 25 16:39:40 2019 GMT
FileName= /etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem
notAfter=Dec  9 10:55:38 2017 GMT
FileName= /etc/pki/consumer/cert.pem
""".strip()

CRT4 = """
notAfter=May 25 16:39:40 2019 GMT
FileName= /etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem
unable to load certificate
140463633168248:error:0906D06C:PEM routines:PEM_read_bio:no start line:pem_lib.c:701:Expecting: TRUSTED CERTIFICATE
notAfter=Dec  9 10:55:38 2017 GMT
FileName= /etc/pki/consumer/cert.pem
notAfter=Jan  1 04:59:59 2022 GMT
""".strip()

CRT5 = """
notAfter=May 25 16:39:40 2019 GMT
FileName= /etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem
notAfter=Dec  9 10:55:38 2017 GMT
unable to load certificate
140463633168248:error:0906D06C:PEM routines:PEM_read_bio:no start line:pem_lib.c:701:Expecting: TRUSTED CERTIFICATE
FileName= /etc/pki/consumer/cert.pem
notAfter=Jan  1 04:59:59 2022 GMT
""".strip()

CRT6 = """
notAfter=May 25 16:39:40 2019
FileName= /etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem
notAfter=Dec  9 10:55:38 20 GMT
FileName= /etc/pki/consumer/cert.pem
""".strip()

PATH1 = "/etc/origin/node/cert.pem"


def test_certificates_enddate():

    Cert1 = CertificatesEnddate(context_wrap(CRT1))
    assert PATH1 in Cert1.certificates_path
    assert Cert1.get_expiration_date(PATH1) == datetime(2019, 05, 25, 16, 39, 40)

    Cert2 = CertificatesEnddate(context_wrap(CRT2))
    assert Cert2.certificates_path == []

    Cert3 = CertificatesEnddate(context_wrap(CRT3))
    assert (Cert3.certificates_path == [
            '/etc/pki/consumer/cert.pem',
            '/etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem'])

    Cert4 = CertificatesEnddate(context_wrap(CRT4))
    assert (Cert4.certificates_path == [
            '/etc/pki/consumer/cert.pem',
            '/etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem'])

    Cert5 = CertificatesEnddate(context_wrap(CRT5))
    assert (Cert5.certificates_path == [
            '/etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem'])


class TestCertificatesEnddateRaise(unittest.TestCase):
    def test_certificates_enddate_raise(self):
        Cert6 = CertificatesEnddate(context_wrap(CRT6))
        assert (Cert6.certificates_path == [
                '/etc/pki/consumer/cert.pem',
                '/etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem'])
        with self.assertRaises(Exception):
            Cert6.get_expiration_date('/etc/pki/consumer/cert.pem')
