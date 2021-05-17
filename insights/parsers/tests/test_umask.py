import doctest
import pytest
from insights.parsers import umask
from insights.parsers.umask import Umask
from insights.parsers import SkipException
from insights.tests import context_wrap


UMASK_DATA = """
u=rwx,g=rx,o=rx
""".strip()

UMASK_NO_DATA = """
""".strip()


def test_umask():
    umask_obj = Umask(context_wrap(UMASK_DATA))
    assert umask_obj.user == 'rwx'
    assert umask_obj.group == 'rx'
    assert umask_obj.other == 'rx'

    with pytest.raises(SkipException) as exc:
        umask_obj = Umask(context_wrap(UMASK_NO_DATA))
        assert umask_obj is not None
    assert 'No Contents' in str(exc)


def test_modinfo_doc_examples():
    env = {'umask_obj': Umask(context_wrap(UMASK_DATA))}
    failed, total = doctest.testmod(umask, globs=env)
    assert failed == 0
