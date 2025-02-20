import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import filefrag
from insights.parsers.filefrag import Filefrag
from insights.tests import context_wrap

FILEFRAG_CONTENT = """
open: No such file or directory
/boot/grub2/grubenv: 1 extent found
/test1: unknow extent found
/test2 unknow extent found
""".strip()

FILEFRAG_CONTENT_NO_FILE = """
open: No such file or directory
""".strip()

FILEFRAG_CONTENT_ERROR = """
""".strip()

DOC_CONTENT = """
open: No such file or directory
/boot/grub2/grubenv: 1 extent found
""".strip()


def test_filefrag_1():
    results = Filefrag(context_wrap(FILEFRAG_CONTENT))
    assert results['/boot/grub2/grubenv'] == 1
    assert results.unparsed_lines == ['/test1: unknow extent found', '/test2 unknow extent found']


def test_filefrag_errors_1():
    with pytest.raises(SkipComponent):
        Filefrag(context_wrap(FILEFRAG_CONTENT_NO_FILE))


def test_filefrag_errors_2():
    with pytest.raises(SkipComponent):
        Filefrag(context_wrap(FILEFRAG_CONTENT_ERROR))


def test_doc_examples():
    env = {
            'filefrag': Filefrag(context_wrap(DOC_CONTENT)),
          }
    failed, total = doctest.testmod(filefrag, globs=env)
    assert failed == 0
