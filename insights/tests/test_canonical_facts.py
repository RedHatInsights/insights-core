import uuid
from insights.combiners.cloud_instance import CloudInstance
from insights.combiners.cloud_provider import CloudProvider
from insights.parsers.aws_instance_id import AWSInstanceIdDoc
from insights.parsers.installed_rpms import InstalledRpms
from insights.tests import context_wrap
from insights.tests.combiners.test_cloud_provider import RPMS_AWS
from insights.tests.parsers.test_aws_instance_id import AWS_ID_DOC
from insights.util.canonical_facts import (
    _filter_falsy, _safe_parse, canonical_facts, IPs, valid_ipv4_address_or_None,
    valid_mac_addresses, valid_uuid_or_None)


def test_identity():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar"})


def test_drops_none():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar", "baz": None})


def test_drops_empty_list():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar", "baz": []})


UUID_VALID = str(uuid.uuid4())
UUID_INVALID = 'invalid uuid'


def test_valid_uuid_or_None():
    result = valid_uuid_or_None(UUID_VALID)
    assert result == UUID_VALID
    result = valid_uuid_or_None(UUID_INVALID)
    assert result is None


IPV4_VALID = [
    '192.168.1.1',
    '1.1.1.1',
    '10.110.1.254',
    '0.0.0.0',
]
IPV4_INVALID = [
    '4001:631:51:a066:250:56ff:1ea7:1696',
    '0.0',
    '192.168',
    'abc',
]


def test_valid_ipv4_address_or_None():
    for ip in IPV4_VALID:
        result = valid_ipv4_address_or_None(ip)
        assert result == ip, 'Failed valid IP address {}'.format(ip)
    for ip in IPV4_INVALID:
        result = valid_ipv4_address_or_None(ip)
        assert result is None, 'Failed invalid IP address {}'.format(ip)


class HasContent():
    def __init__(self, content=None):
        self.content = [content, ] if content is not None else []


MACS_VALID = [
    HasContent('aa:26:28:12:22:1a'),
    HasContent('   aa:26:28:12:22:1a   '),
    HasContent('aa:26:28:12:22:2a'),
    HasContent('aa:26:28:12:22:3a'),
    HasContent('00:00:00:00:00:00'),
]
MACS_INVALID = [
    HasContent('aa:26:28:12:22:1a:aa:26:28:12:22:1a'),
    HasContent('# aa:26:28:12:22:1a'),
    HasContent('00:00:00:00'),
]


def test_valid_mac_addresses():
    result = valid_mac_addresses(MACS_VALID)
    assert result == [m.content[0].strip() for m in MACS_VALID]
    result = valid_mac_addresses(MACS_INVALID)
    assert result == []


HOSTNAME_I_VALID = '192.168.1.71 10.88.0.1 172.17.0.1 172.18.0.1 10.10.121.131\n'
HOSTNAME_I_INVALID = '19f.168.1.71 0.0 2307:f1c0:ff13:f036:c0::214 f001:1a98:380:4::1d 2f07:a160:ff01:2092:e32:a5ff:ff37:7114'


def test_IPs():
    ips = IPs(context_wrap(HOSTNAME_I_VALID))
    assert ips.data == HOSTNAME_I_VALID.strip().split()
    ips = IPs(context_wrap(HOSTNAME_I_INVALID))
    assert ips.data == []


def test_safe_parse():
    result = _safe_parse(HasContent('some content'))
    assert result == 'some content'
    result = _safe_parse(HasContent())
    assert result is None
    result = _safe_parse(None)
    assert result is None


def test_canonical_facts_providers():
    rpms = InstalledRpms(context_wrap(RPMS_AWS))
    _id = AWSInstanceIdDoc(context_wrap(AWS_ID_DOC))
    cp = CloudProvider(rpms, None, None, None)
    ci = CloudInstance(cp, _id, None, None, None, None)
    ret = canonical_facts(None, None, None, None, None, None, None, ci)
    assert ret.get('provider_id') == 'i-1234567890abcdef0'
    assert ret.get('provider_type') == 'aws'
