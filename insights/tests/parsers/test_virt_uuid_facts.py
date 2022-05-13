import doctest

from insights.parsers import virt_uuid_facts
from insights.tests.parsers import skip_exception_check
from insights.parsers.virt_uuid_facts import VirtUuidFacts
from insights.tests import context_wrap


VIRT_UUID_FACTS = """
{"virt.uuid": "4546B285-6C41-5D6R-86G5-0BFR4B3625FS", "uname.machine": "x86"}
""".strip()


def test_virt_uuid_facts():
    result = VirtUuidFacts(context_wrap(VIRT_UUID_FACTS))

    assert result.data == {
            'virt.uuid': '4546B285-6C41-5D6R-86G5-0BFR4B3625FS',
            "uname.machine": "x86"
    }
    assert result.data['virt.uuid'] == '4546B285-6C41-5D6R-86G5-0BFR4B3625FS'


def test_virt_uuid_facts_empty():
    assert 'Empty output.' in skip_exception_check(VirtUuidFacts)


def test_virt_uuid_facts_doc_examples():
    env = {
        'VirtUuidFacts': VirtUuidFacts,
        'virt_uuid_facts': VirtUuidFacts(context_wrap(VIRT_UUID_FACTS)),
    }
    failed, total = doctest.testmod(virt_uuid_facts, globs=env)
    assert failed == 0
