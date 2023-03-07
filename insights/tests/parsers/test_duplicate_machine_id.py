from insights.core.exceptions import SkipException
import pytest
import doctest
from insights.parsers import duplicate_machine_id
from insights.tests import context_wrap

DUPLICATE_MACHINE_ID = """dc194312-8cdd-4e75-8cf1-2094bf666f45"""

WRONG_CONTENT_1 = ""

WRONG_CONTENT_2 = """
dc194312-8cdd-4e75-8cf1-2094bf666f25
dc194312-8cdd-4e75-8cf1-2094bf666asd
""".strip()


def test_duplicate_id():
    machine_obj = duplicate_machine_id.DuplicateMachineId(context_wrap(DUPLICATE_MACHINE_ID))
    assert machine_obj.duplicate_machine_id == 'dc194312-8cdd-4e75-8cf1-2094bf666f45'


def test_exception():
    with pytest.raises(SkipException):
        duplicate_machine_id.DuplicateMachineId(context_wrap(WRONG_CONTENT_1))

    with pytest.raises(SkipException):
        duplicate_machine_id.DuplicateMachineId(context_wrap(WRONG_CONTENT_2))


def test_doc():
    machine_obj = duplicate_machine_id.DuplicateMachineId(context_wrap(DUPLICATE_MACHINE_ID))
    env = {'machine_id_obj': machine_obj}
    failed, total = doctest.testmod(duplicate_machine_id, globs=env)
    assert failed == 0
