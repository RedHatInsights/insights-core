from falafel.mappers.certificates_enddate import CertificatesEnddate
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

CRT3 = """
notAfter=Mar 21 08:32:37 2017 GMT
""".strip()

CRT3_PATH = "etc/pki/ovirt-engine/ca.pem"

CRT4 = ""

CRT5 = """
InvalidVaule=I am not sure this will happen or not .
""".strip()

CRT5_PATH = "/etc/pki/what-ever"

# These are the conditions that the pre_command 'crt' send the openssl bad input.
# 'crt' is a not a vaild certificate file.
CRT6 = """
unable to load certificate
140549596768160:error:0906D06C:PEM routines:PEM_read_bio:no start line:pem_lib.c:703:Expecting: TRUSTED CERTIFICATE
""".strip()

CRT6_PATH = "/etc/pki/ca-trust/source/README"

# 'crt' is the stderr of find command.
# eg. "/usr/bin/find: '/etc/origin/master': No such file or directory"
CRT7 = """
Unknown option '/etc/origin/master':
usage: x509 args
 -inform arg     - input format - default PEM (one of DER, NET or PEM)
 -outform arg    - output format - default PEM (one of DER, NET or PEM)
...
""".strip()

# Path like this? Not sure
CRT7_PATH = "/usr/bin/find: '/etc/origin/master': No such file or directory"


def test_certificates_enddate():
    Cert1 = CertificatesEnddate(context_wrap(CRT1, path=CRT1_PATH))
    assert Cert1.file_name == 'ca.crt'
    assert Cert1.get_expiration_date() == datetime.datetime(2021, 11, 24, 2, 58, 22)

    Cert2 = CertificatesEnddate(context_wrap(CRT2, path=CRT2_PATH))
    assert Cert2.file_name == 'server.crt'
    assert Cert2.get_expiration_date() == datetime.datetime(2018, 11, 25, 3, 2, 4)

    Cert3 = CertificatesEnddate(context_wrap(CRT3, path=CRT3_PATH))
    assert Cert3.file_path == CRT3_PATH
    assert Cert3.file_name == 'ca.pem'
    assert Cert3.get_expiration_date() == datetime.datetime(2017, 03, 21, 8, 32, 37)

    Cert4 = CertificatesEnddate(context_wrap(CRT4, path=CRT3_PATH))
    assert Cert4.file_path == CRT3_PATH
    assert Cert4.file_name == 'ca.pem'
    assert Cert4.get_expiration_date() is None

    Cert5 = CertificatesEnddate(context_wrap(CRT5, path=CRT5_PATH))
    assert Cert5.file_path == CRT5_PATH
    assert Cert5.file_name == 'what-ever'
    # assert Cert5.get_expiration_date() # will get exception here as expected

    Cert6 = CertificatesEnddate(context_wrap(CRT6, path=CRT6_PATH))
    assert Cert6.file_name == 'README'
    assert Cert6.get_expiration_date() is None

    Cert7 = CertificatesEnddate(context_wrap(CRT7, path=CRT7_PATH))
    assert Cert7.file_path == CRT7_PATH
    assert Cert7.file_name == 'master\': No such file or directory'
    assert Cert7.get_expiration_date() is None
