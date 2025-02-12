import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import filefrag
from insights.parsers.filefrag import FilefragGrubenv
from insights.tests import context_wrap

FILEFRAG_GRUBENV = """
/boot/grub2/grubenv: 1 extent found
""".strip()

FILEFRAG_GRUBENV_ERROR = """
open: No such file or directory
""".strip()

FILEFRAG_GRUBENV_ERROR2 = """
/boot/grub2/grubenv: unknow extent found
""".strip()


def test_wc_proc_1_mountinfo():
    results = FilefragGrubenv(context_wrap(FILEFRAG_GRUBENV))
    assert results.extents == 1


def test_wc_proc_1_mountinfo_errors():
    with pytest.raises(SkipComponent) as ex:
        FilefragGrubenv(context_wrap(FILEFRAG_GRUBENV_ERROR))
        assert FILEFRAG_GRUBENV_ERROR in str(ex)

    with pytest.raises(SkipComponent) as ex:
        FilefragGrubenv(context_wrap(FILEFRAG_GRUBENV_ERROR2))
        assert FILEFRAG_GRUBENV_ERROR2 in str(ex)


def test_doc_examples():
    env = {
            'grubenv': FilefragGrubenv(context_wrap(FILEFRAG_GRUBENV)),
          }
    failed, total = doctest.testmod(filefrag, globs=env)
    assert failed == 0
