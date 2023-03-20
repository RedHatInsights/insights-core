import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import gfs2_file_system_block_size
from insights.tests import context_wrap

BLOCK_SIZE_OUTPUT = """
4096
""".strip()

BLOCK_SIZE_OUTPUT_2 = """
abc
""".strip()

BLOCK_SIZE_OUTPUT_3 = """
512
""".strip()

BLOCK_SIZE_OUTPUT_4 = """
4096
512
""".strip()

BLOCK_SIZE_OUTPUT_5 = """
stat: missing operand
Try 'stat --help' for more information.
""".strip()


def test_exp():
    with pytest.raises(SkipComponent):
        gfs2_file_system_block_size.GFS2FileSystemBlockSize(context_wrap(BLOCK_SIZE_OUTPUT_2))
    with pytest.raises(SkipComponent):
        gfs2_file_system_block_size.GFS2FileSystemBlockSize(context_wrap(BLOCK_SIZE_OUTPUT_4))
    with pytest.raises(SkipComponent):
        gfs2_file_system_block_size.GFS2FileSystemBlockSize(context_wrap(BLOCK_SIZE_OUTPUT_5))


def test_doc():
    env = {
            'gfs2_mp': gfs2_file_system_block_size.GFS2FileSystemBlockSize(context_wrap(BLOCK_SIZE_OUTPUT))
          }
    failed, total = doctest.testmod(gfs2_file_system_block_size, globs=env)
    assert failed == 0


def test_other_size():
    gfs2 = gfs2_file_system_block_size.GFS2FileSystemBlockSize(context_wrap(BLOCK_SIZE_OUTPUT_3))
    assert gfs2.block_size == 512
