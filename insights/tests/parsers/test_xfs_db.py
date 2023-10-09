from insights.core.exceptions import SkipComponent
from insights.parsers import xfs_db
from insights.parsers.xfs_db import XFSDbFrag
from insights.parsers.xfs_db import XFSDbFreesp
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

XFS_DB_FREESP_1 = """
   from      to extents  blocks    pct
      1       1      16      16   0.01
      2       3       1       2   0.00
     64     127       1     103   0.04
  32768   65536       4  231135  99.95
""".strip()

XFS_DB_FREESP_2 = """
   from      to extents  blocks    pct
""".strip()

XFS_DB_FREESP_3 = """
# some error message
meaningless line 1
   from      to extents  blocks    pct
      1       1      16      16   0.01
      2       3       1       2   0.00
     64     127       1     103   0.04
  32768   65536       4  231135  99.95
""".strip()

XFS_DB_FREESP_ERR_1 = """
   from      to extents  blocks
      1       1      16      16
      2       3       1       2
""".strip()

XFS_DB_FREESP_ERR_2 = """
   from      to extents  blocks   pct   test
""".strip()


def test_xfs_db_frag():
    result = XFSDbFrag(context_wrap(XFS_DB_FRAG_1))
    assert result.fragmentation_factor == "58.28%"

    result = XFSDbFrag(context_wrap(XFS_DB_FRAG_2))
    assert result.fragmentation_factor == "98.93%"


def test_xfs_db_frag_err():
    with pytest.raises(SkipComponent) as e:
        XFSDbFrag(context_wrap(XFS_DB_FRAG_ERR_1))
    assert "Invalid output of xfs fragmentation" in str(e)

    with pytest.raises(SkipComponent) as e:
        XFSDbFrag(context_wrap(XFS_DB_FRAG_ERR_2))
    assert "Invalid output of xfs fragmentation" in str(e)


def test_xfs_db_freesp():
    result = XFSDbFreesp(context_wrap(XFS_DB_FREESP_1))
    assert len(result.free_stat) == 4
    assert result.free_stat[-1]['to'] == '65536'
    search_result = result.search(pct="0.00")
    assert len(search_result) == 1
    assert search_result[0]['from'] == '2'

    result = XFSDbFreesp(context_wrap(XFS_DB_FREESP_2))
    assert result.free_stat == []

    result = XFSDbFreesp(context_wrap(XFS_DB_FREESP_3))
    assert len(result.free_stat) == 4
    assert result.free_stat[-1]['to'] == '65536'


def test_xfs_db_freesp_err():
    with pytest.raises(SkipComponent) as e:
        XFSDbFreesp(context_wrap(XFS_DB_FREESP_ERR_1))
    assert "Invalid output of xfs free space" in str(e)

    with pytest.raises(SkipComponent) as e:
        XFSDbFreesp(context_wrap(XFS_DB_FREESP_ERR_2))
    assert "Invalid output of xfs free space" in str(e)


def test_xfs_db_doc_examples():
    env = {
        'xfs_db_frag': XFSDbFrag(context_wrap(XFS_DB_FRAG_1)),
        'xfs_db_freesp': XFSDbFreesp(context_wrap(XFS_DB_FREESP_1))
    }
    failed, total = doctest.testmod(xfs_db, globs=env)
    assert failed == 0
