import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import etc_machine_id
from insights.parsers.etc_machine_id import EtcMachineId
from insights.tests import context_wrap

ETC_MACHINE_ID = """
4f3fbfda59ff4aea969255a73342d439
""".strip()

ETC_MACHINE_ID_ERROR = """
4f3fbfda59ff4aea969255a73342d439
4f3fbfda59ff4aea969255a7334
""".strip()


def test_etcd_conf_empty():
    with pytest.raises(SkipComponent):
        EtcMachineId(context_wrap(''))


def test_etcd_conf_error():
    with pytest.raises(SkipComponent):
        EtcMachineId(context_wrap(ETC_MACHINE_ID_ERROR))


def test_etcd_conf():
    machine_id = EtcMachineId(context_wrap(ETC_MACHINE_ID))
    assert machine_id.machine_id == '4f3fbfda59ff4aea969255a73342d439'


def test_etcd_conf_documentation():
    env = {
        'machine_id': EtcMachineId(context_wrap(ETC_MACHINE_ID)),
    }
    failed, total = doctest.testmod(etc_machine_id, globs=env)
    assert failed == 0
