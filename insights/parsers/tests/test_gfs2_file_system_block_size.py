from insights.parsers import gfs2_file_system_block_size
from insights.tests import context_wrap
from insights.parsers import SkipException
import pytest
import doctest

BLOCK_SIZE_OUTPUT = """
4096
""".strip()

BLOCK_SIZE_OUTPUT_2 = """
abc
""".strip()


def test_exp():
    with pytest.raises(SkipException):
        gfs2_file_system_block_size.GFS2FileSystemBlockSize(context_wrap(BLOCK_SIZE_OUTPUT_2))


def test_doc():
    env = {
            'gfs2_mp': gfs2_file_system_block_size.GFS2FileSystemBlockSize(context_wrap(BLOCK_SIZE_OUTPUT))
          }
    failed, total = doctest.testmod(gfs2_file_system_block_size, globs=env)
    assert failed == 0
