import uuid

from insights.core.plugins import make_metadata
from insights.specs import Specs
from insights.tests import InputData, archive_provider
from insights.tests.combiners.test_cloud_provider import RPMS_AWS
from insights.tests.parsers.test_aws_instance_id import AWS_ID_DOC
from insights.tests.parsers.test_client_metadata import MACHINE_ID
from insights.tests.parsers.test_etc_machine_id import ETC_MACHINE_ID
from insights.tests.parsers.test_hostname import HOSTNAME_FULL
from insights.tests.parsers.test_ip import HOSTNAME_I
from insights.util.canonical_facts import _filter_falsy, canonical_facts


def test_identity():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar"})


def test_drops_none():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar", "baz": None})


def test_drops_empty_list():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar", "baz": []})


@archive_provider(canonical_facts)
def integration_test_hit():
    data = InputData()
    data.add(Specs.installed_rpms, RPMS_AWS)
    data.add(Specs.aws_instance_id_doc, AWS_ID_DOC)
    data.add(Specs.hostname, HOSTNAME_FULL)
    data.add(Specs.ip_addresses, HOSTNAME_I)
    data.add(Specs.etc_machine_id, ETC_MACHINE_ID)
    data.add(Specs.machine_id, MACHINE_ID)
    expected = make_metadata(
        insights_id=MACHINE_ID,
        machine_id=str(uuid.UUID(ETC_MACHINE_ID)),
        ip_addresses=['10.230.230.220', '10.230.0.1'],
        fqdn=HOSTNAME_FULL,
        provider_id='i-1234567890abcdef0',
        provider_type='aws')

    yield data, expected
