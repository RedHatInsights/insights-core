import pytest
import os
import shutil

from insights import dr, HostContext
from insights.core import filters
from insights.core.dr import SkipComponent
from insights.specs import Specs
from insights.specs.datasources.certificates import get_certificate_info, cert_and_path


CONTENT_1 = [
    'issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
    'notBefore=Dec  7 07:02:33 2022 GMT',
    'notAfter=Jan 18 07:02:33 2038 GMT',
    'subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
]

CONTENT_2 = [
    'issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
    'notBefore=Dec  7 07:02:33 2042 GMT',
    'notAfter=Jan 18 07:02:33 2048 GMT',
    'subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com',
]


class FakeContext(HostContext):
    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        if 'test_abc' in cmd:
            return (0, CONTENT_1.copy())
        elif 'test_def' in cmd:
            return (0, CONTENT_2.copy())
        else:
            return (-1, [])

        raise Exception()


def setup_function(func):
    if Specs.certificates_info in filters._CACHE:
        del filters._CACHE[Specs.certificates_info]
    if Specs.certificates_info in filters.FILTERS:
        del filters.FILTERS[Specs.certificates_info]

    if func is test_cert_and_path:
        filters.add_filter(Specs.certificates_info, ['/tmp/test_abc.pem', '/tmp/test_pki'])
    elif func is test_cert_and_path_not_found:
        filters.add_filter(Specs.certificates_info, ['not_found'])


def teardown_function(func):
    if func is test_cert_and_path or func is test_cert_and_path_not_found:
        del filters.FILTERS[Specs.certificates_info]


def test_get_certificate_info_file():
    ctx = FakeContext()
    test_pem = '/tmp/test_abc.pem'
    open(test_pem, 'a').close()
    result = get_certificate_info(ctx, test_pem)
    assert len(result) == 5
    assert result[1] == 'notBefore=Dec  7 07:02:33 2022 GMT'
    assert result[-1] == 'FileName= {}'.format(test_pem)
    os.remove(test_pem)


def test_get_certificate_info_dir():
    ctx = FakeContext()
    test_dir = '/tmp/test_pki'
    os.makedirs(test_dir)
    open(os.path.join(test_dir, 'test_abc.pem'), 'a').close()
    open(os.path.join(test_dir, 'test_def.pem'), 'a').close()
    result = get_certificate_info(ctx, test_dir)
    assert len(result) == 10
    assert result[1] == 'notBefore=Dec  7 07:02:33 2042 GMT'
    assert result[4] == 'FileName= {}'.format(os.path.join(test_dir, 'test_def.pem'))
    assert result[6] == 'notBefore=Dec  7 07:02:33 2022 GMT'
    assert result[-1] == 'FileName= {}'.format(os.path.join(test_dir, 'test_abc.pem'))
    shutil.rmtree(test_dir)


def test_get_certificate_info_ng():
    ctx = FakeContext()
    test_pem = '/tmp/test_test.pem'
    open(test_pem, 'a').close()
    result = get_certificate_info(ctx, test_pem)
    assert result == []
    os.remove(test_pem)


def test_get_certificate_info_no_such_fd():
    ctx = FakeContext()
    test_dir = '/tmp/test_pki'
    result = get_certificate_info(ctx, test_dir)
    assert result == []


def test_cert_and_path():
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    test_pem = '/tmp/test_abc.pem'
    open(test_pem, 'a').close()
    test_dir = '/tmp/test_pki'
    os.makedirs(test_dir)
    open(os.path.join(test_dir, 'test_def.pem'), 'a').close()

    result = cert_and_path(broker)
    assert sorted(result.content) == sorted(CONTENT_1 + ['FileName= /tmp/test_abc.pem'] + CONTENT_2 + ['FileName= /tmp/test_pki/test_def.pem'])

    os.remove(test_pem)
    shutil.rmtree(test_dir)


def test_cert_and_path_no_filters():
    test_pem = '/tmp/test_abc.pem'
    open(test_pem, 'a').close()
    test_dir = '/tmp/test_pki'
    os.makedirs(test_dir)
    open(os.path.join(test_dir, 'test_def.pem'), 'a').close()

    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    with pytest.raises(SkipComponent):
        cert_and_path(broker)

    os.remove(test_pem)
    shutil.rmtree(test_dir)


def test_cert_and_path_not_found():
    test_pem = '/tmp/test_abc.pem'
    open(test_pem, 'a').close()
    test_dir = '/tmp/test_pki'
    os.makedirs(test_dir)
    open(os.path.join(test_dir, 'test_def.pem'), 'a').close()

    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    with pytest.raises(SkipComponent):
        cert_and_path(broker)

    os.remove(test_pem)
    shutil.rmtree(test_dir)
