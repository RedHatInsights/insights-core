import doctest
import pytest

from insights.core.exceptions import ContentException, ParseException, SkipComponent
from insights.parsers import puppet_ca_cert_expire_date
from insights.tests import context_wrap


PUPPET_CERT_EXPIRE_INFO = '''
notAfter=Dec  4 07:04:05 2035 GMT
'''

WRONG_PUPPET_CERT_INFO_1 = '''
Can't open /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem for reading, No such file or directory
140033749546816:error:02001002:system library:fopen:No such file or directory:crypto/bio/bss_file.c:69:fopen('/etc/puppetlabs/puppet/ssl/ca/ca_crt.pem','r')
140033749546816:error:2006D080:BIO routines:BIO_new_file:no such file:crypto/bio/bss_file.c:76:
unable to load certificate
'''

WRONG_PUPPET_CERT_INFO_2 = '''
notAfter=Mon Jan  4 02:31:28 EST 202
'''

WRONG_PUPPET_CERT_INFO_3 = '''
Mon Jan  4 02:31:28 EST 202
'''

WRONG_PUPPET_CERT_INFO_4 = '''
abc=def
'''


def test_HTL_doc_examples():
    date_info = puppet_ca_cert_expire_date.PuppetCertExpireDate(context_wrap(PUPPET_CERT_EXPIRE_INFO))
    globs = {
        'date_info': date_info
    }
    failed, tested = doctest.testmod(puppet_ca_cert_expire_date, globs=globs)
    assert failed == 0


def test_parser():
    date_info = puppet_ca_cert_expire_date.PuppetCertExpireDate(context_wrap(PUPPET_CERT_EXPIRE_INFO))
    assert 'notAfter' in date_info
    assert date_info['notAfter'].str == 'Dec  4 07:04:05 2035'


def test_wrong_output():
    with pytest.raises(ContentException):
        puppet_ca_cert_expire_date.PuppetCertExpireDate(context_wrap(WRONG_PUPPET_CERT_INFO_1))
    with pytest.raises(ParseException):
        puppet_ca_cert_expire_date.PuppetCertExpireDate(context_wrap(WRONG_PUPPET_CERT_INFO_3))
    with pytest.raises(ParseException):
        puppet_ca_cert_expire_date.PuppetCertExpireDate(context_wrap(WRONG_PUPPET_CERT_INFO_2))
    with pytest.raises(SkipComponent):
        puppet_ca_cert_expire_date.PuppetCertExpireDate(context_wrap(WRONG_PUPPET_CERT_INFO_4))
