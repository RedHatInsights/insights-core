import doctest
import pytest

from insights.tests import context_wrap
from insights.parsers import machine_id
from insights.core.exceptions import SkipException

MACHINE_ID_CONTENT = """dc194312-8cdd-4e75-8cf1-2094bf666f45 hostname1,hostname2"""

WRONG_CONTENT_1 = ""

WRONG_CONTENT_2 = """
dc194312-8cdd-4e75-8cf1-2094bf666f25 hostname1,hostname2
dc194312-8cdd-4e75-8cf1-2094bf666asd hostname3,hostname4
""".strip()

WRONG_CONTENT_3 = """
dc194312-8cdd-4e75-8cf1-2094bf666f25
""".strip()


def test_duplicate_id():
    machine_obj = machine_id.DuplicateMachine(context_wrap(MACHINE_ID_CONTENT))
    assert machine_obj.duplicate_id == 'dc194312-8cdd-4e75-8cf1-2094bf666f45'
    assert machine_obj.hostnames == ['hostname1', 'hostname2']


def test_exception():
    with pytest.raises(SkipException):
        machine_id.DuplicateMachine(context_wrap(WRONG_CONTENT_1))

    with pytest.raises(SkipException):
        machine_id.DuplicateMachine(context_wrap(WRONG_CONTENT_2))

    with pytest.raises(SkipException):
        machine_id.DuplicateMachine(context_wrap(WRONG_CONTENT_3))


def test_doc():
    machine_obj = machine_id.DuplicateMachine(context_wrap(MACHINE_ID_CONTENT))
    env = {'machine_id_obj': machine_obj}
    failed, total = doctest.testmod(machine_id, globs=env)
    assert failed == 0
