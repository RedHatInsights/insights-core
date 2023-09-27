from insights.core.exceptions import SkipComponent
from insights.parsers import xfs_db
from insights.parsers.xfs_db import XFSDbFrag
from insights.tests import context_wrap
import doctest
import pytest

XFS_DB_FRAG_1 = """
actual 39954415, ideal 16668437, fragmentation factor 58.28%
Note, this number is largely meaningless.
Files on this filesystem average 1.00 extents per file
""".strip()

XFS_DB_FRAG_2 = """
invalid numrecs (27111) in bmapbtd block
invalid numrecs (4716) in bmapbtd block
invalid numrecs (58978) in bmapbtd block
actual 1034793, ideal 11024, fragmentation factor 98.93%
""".strip()

XFS_DB_FRAG_ERR_1 = """
""".strip()

XFS_DB_FRAG_ERR_2 = """
invalid numrecs (27111) in bmapbtd block
invalid numrecs (4716) in bmapbtd block
invalid numrecs (58978) in bmapbtd block
""".strip()


def test_xfs_db_frag():
    result = XFSDbFrag(context_wrap(XFS_DB_FRAG_1))
    assert result.fragmentation_factor == "58.28%"

    result = XFSDbFrag(context_wrap(XFS_DB_FRAG_2))
    assert result.fragmentation_factor == "98.93%"


def test_xfs_db_err():
    with pytest.raises(SkipComponent) as e:
        XFSDbFrag(context_wrap(XFS_DB_FRAG_ERR_1))
    assert "Invalid output of xfs fragmentation" in str(e)

    with pytest.raises(SkipComponent) as e:
        XFSDbFrag(context_wrap(XFS_DB_FRAG_ERR_2))
    assert "Invalid output of xfs fragmentation" in str(e)


def test_xfs_db_frag_doc_examples():
    env = {
        'xfs_db_frag': XFSDbFrag(context_wrap(XFS_DB_FRAG_1))
    }
    failed, total = doctest.testmod(xfs_db, globs=env)
    assert failed == 0
