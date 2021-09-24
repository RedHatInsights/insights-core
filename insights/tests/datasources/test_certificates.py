import pytest
import os
import shutil

from insights import dr, HostContext
from insights.core import filters
from insights.core.dr import SkipComponent
from insights.specs import Specs
from insights.specs.datasources import certificates
from insights.specs.datasources.certificates import get_certificate_info, cert_and_path


CONTENT_1 = [
    'issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
    'notBefore=Dec 7 07:02:33 2022 GMT',
    'notAfter=Jan 18 07:02:33 2038 GMT',
    'subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
]

CONTENT_2 = [
    'issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
    'notBefore=Dec 7 07:02:33 2042 GMT',
    'notAfter=Jan 18 07:02:33 2048 GMT',
    'subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
]

test_dir1 = '/tmp/test_pki'
test_dir2 = '/tmp/test_test'
test_pem1 = '/tmp/test_abc.pem'
test_pem2 = '/tmp/test_test.pem'


class FakeContext(HostContext):
    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        if 'test_abc' in cmd:
            return (0,
                [
                    'issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
                    'notBefore=Dec 7 07:02:33 2022 GMT',
                    'notAfter=Jan 18 07:02:33 2038 GMT',
                    'subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
                ]
            )
        elif 'test_def' in cmd:
            return (0,
                [
                    'issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
                    'notBefore=Dec 7 07:02:33 2042 GMT',
                    'notAfter=Jan 18 07:02:33 2048 GMT',
                    'subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
                ]
            )
        else:
            return (-1, [])

        raise Exception()


def setup_function(func):
    if Specs.certificates_info in filters._CACHE:
        del filters._CACHE[Specs.certificates_info]
    if Specs.certificates_info in filters.FILTERS:
        del filters.FILTERS[Specs.certificates_info]

    if func is test_cert_and_path or func is test_permitted_paths:
        filters.add_filter(Specs.certificates_info, ['/tmp/test_abc.pem', '/tmp/test_pki'])
    elif func is test_cert_and_path_not_found:
        filters.add_filter(Specs.certificates_info, ['not_found'])

    certificates.UNIT_TEST = True
    os.makedirs(test_dir1)
    open(os.path.join(test_dir1, 'test_abc.pem'), 'a').close()
    open(os.path.join(test_dir1, 'test_def.pem'), 'a').close()
    open(test_pem1, 'a').close()
    open(test_pem2, 'a').close()


def teardown_function(func):
    if func is test_cert_and_path or func is test_cert_and_path_not_found:
        del filters.FILTERS[Specs.certificates_info]
    shutil.rmtree(test_dir1)
    os.remove(test_pem1)
    os.remove(test_pem2)
    certificates.UNIT_TEST = False


def test_get_certificate_info_file():
    ctx = FakeContext()
    result = get_certificate_info(ctx, test_pem1)
    assert len(result) == 5
    assert result[1] == 'notBefore=Dec 7 07:02:33 2022 GMT'
    assert result[-1] == 'FileName= {0}'.format(test_pem1)


def test_get_certificate_info_dir():
    ctx = FakeContext()
    result = get_certificate_info(ctx, test_dir1)
    assert len(result) == 10
    assert sorted(result) == sorted(CONTENT_1 + ['FileName= /tmp/test_pki/test_abc.pem'] + CONTENT_2 + ['FileName= /tmp/test_pki/test_def.pem'])


def test_get_certificate_info_ng():
    ctx = FakeContext()
    result = get_certificate_info(ctx, test_pem2)
    assert result == []


def test_get_certificate_info_no_such_fd():
    ctx = FakeContext()
    result = get_certificate_info(ctx, test_dir2)
    assert result == []


def test_cert_and_path():
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    result = cert_and_path(broker)
    assert sorted(result.content) == sorted(
            CONTENT_1 +
            CONTENT_1 +
            CONTENT_2 +
            ['FileName= /tmp/test_abc.pem'] +
            ['FileName= /tmp/test_pki/test_abc.pem'] +
            ['FileName= /tmp/test_pki/test_def.pem']
    )


def test_cert_and_path_no_filters():
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    with pytest.raises(SkipComponent):
        cert_and_path(broker)


def test_cert_and_path_not_found():
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    with pytest.raises(SkipComponent):
        cert_and_path(broker)


def test_permitted_paths():
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    certificates.UNIT_TEST = False
    result = cert_and_path(broker)
    # The 'test_dir1' is not collected when not `certificates.UNIT_TEST`
    assert sorted(result.content) == sorted(CONTENT_1 + ['FileName= /tmp/test_abc.pem'])
