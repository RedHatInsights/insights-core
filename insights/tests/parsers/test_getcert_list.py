from insights.tests import context_wrap
from insights.parsers.getcert_list import CertList
from insights.parsers import ParseException

import pytest

CERT_LIST_1 = """
Number of certificates and requests being tracked: 8.
Request ID '20150522133327':
        status: MONITORING
        stuck: no
        key pair storage: type=NSSDB,location='/etc/dirsrv/slapd-EXAMPLE-COM',nickname='Server-Cert',token='NSS Certificate DB',pinfile='/etc/dirsrv/slapd-EXAMPLE-COM/pwdfile.txt'
        certificate: type=NSSDB,location='/etc/dirsrv/slapd-EXAMPLE-COM',nickname='Server-Cert',token='NSS Certificate DB'
        CA: IPA
        issuer: CN=Certificate Authority,O=EXAMPLE.COM
        subject: CN=ldap.example.com,O=EXAMPLE.COM
        expires: 2017-05-22 13:33:27 UTC
        key usage: digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment
        eku: id-kp-serverAuth,id-kp-clientAuth
        pre-save command:
        post-save command: /usr/lib64/ipa/certmonger/restart_dirsrv EXAMPLE-COM
        track: yes
        auto-renew: yes
Request ID '20150522133549':
        status: MONITORING
        stuck: no
        key pair storage: type=NSSDB,location='/etc/httpd/alias',nickname='Server-Cert',token='NSS Certificate DB',pinfile='/etc/httpd/alias/pwdfile.txt'
        certificate: type=NSSDB,location='/etc/httpd/alias',nickname='Server-Cert',token='NSS Certificate DB'
        CA: IPA
        issuer: CN=Certificate Authority,O=EXAMPLE.COM
        subject: CN=ldap.example.com,O=EXAMPLE.COM
        expires: 2017-05-22 13:35:49 UTC
        key usage: digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment
        eku: id-kp-serverAuth,id-kp-clientAuth
        pre-save command:
        post-save command: /usr/lib64/ipa/certmonger/restart_httpd
        track: yes
        auto-renew: yes
"""


def test_getcert_1():
    certs = CertList(context_wrap(CERT_LIST_1, path="sos_commands/ipa/ipa-getcert_list"))

    assert certs.num_tracked == 8
    # Number of actual requests that we see here.
    assert sorted(certs.requests) == sorted(['20150522133327', '20150522133549'])
    # Treated as a pseudo-dict
    assert len(certs) == 2
    assert '20150522133327' in certs
    assert certs['20150522133327']['status'] == 'MONITORING'
    assert certs['20150522133327']['stuck'] == 'no'
    assert certs['20150522133327']['key pair storage'] == "type=NSSDB,location='/etc/dirsrv/slapd-EXAMPLE-COM',nickname='Server-Cert',token='NSS Certificate DB',pinfile='/etc/dirsrv/slapd-EXAMPLE-COM/pwdfile.txt'"
    assert certs['20150522133327']['certificate'] == "type=NSSDB,location='/etc/dirsrv/slapd-EXAMPLE-COM',nickname='Server-Cert',token='NSS Certificate DB'"
    assert certs['20150522133327']['CA'] == 'IPA'
    assert certs['20150522133327']['issuer'] == 'CN=Certificate Authority,O=EXAMPLE.COM'
    assert certs['20150522133327']['subject'] == 'CN=ldap.example.com,O=EXAMPLE.COM'
    assert certs['20150522133327']['expires'] == '2017-05-22 13:33:27 UTC'
    assert certs['20150522133327']['key usage'] == 'digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment'
    assert certs['20150522133327']['eku'] == 'id-kp-serverAuth,id-kp-clientAuth'
    assert certs['20150522133327']['pre-save command'] == ''
    assert certs['20150522133327']['post-save command'] == '/usr/lib64/ipa/certmonger/restart_dirsrv EXAMPLE-COM'
    assert certs['20150522133327']['track'] == 'yes'
    assert certs['20150522133327']['auto-renew'] == 'yes'

    # keyword search tests
    assert certs.search(stuck='no') == [certs['20150522133327'], certs['20150522133549']]


CERT_BAD_1 = """
Number of certificates and requests being tracked: d.
"""

CERT_BAD_2 = """
Number of certificates and requests being tracked: 8.
Request ID '20150522133327':
        status: MONITORING
        stuck: no
Request ID '20150522133327':
        status: MONITORING
        stuck: no
"""


def test_getcert_exceptions():
    with pytest.raises(ParseException) as exc:
        assert CertList(context_wrap(CERT_BAD_1)) is None
    assert 'Incorrectly formatted number of certificates and requests' in str(exc)
    with pytest.raises(ParseException) as exc:
        assert CertList(context_wrap(CERT_BAD_2)) is None
    assert "Found duplicate request ID '20150522133327'" in str(exc)


CERT_BAD_3 = """
Number of certificates and requests being tracked: 2.
Request ID '20150522133327':
        status: MONITORING
        invalid object
"""


def test_getcert_coverage():
    certs = CertList(context_wrap(CERT_BAD_3))
    assert certs
    assert certs.num_tracked == 2
    assert '20150522133327' in certs
    # Lines without a colon get ignored
    assert certs['20150522133327'] == {'status': 'MONITORING'}
