import doctest
from insights.parsers import cifs
from insights.parsers.cifs import CIFSDebugData
from insights.tests import context_wrap


CIFS_DEBUG_DATA_CONTENT = """
DFS origin full path: \\ad.abc.com\DFSROOT\ame1
DFS leaf full path:   \\CVXDFAVB1\DFSRoot\ame1
"""

CIFSDebugData.last_scan('test_dfs_origin_test', 'DFS origin')


def test_cifs_debug_data():
    cifs_dd_obj = CIFSDebugData(context_wrap(CIFS_DEBUG_DATA_CONTENT))

    assert cifs_dd_obj.test_dfs_origin_test
    assert cifs_dd_obj.test_dfs_origin_test.get('raw_message') == "DFS origin full path: \\ad.abc.com\DFSROOT\ame1"


def test_doc():
    env = {
            'cifs_dd_obj': CIFSDebugData(context_wrap(CIFS_DEBUG_DATA_CONTENT))
          }
    failures, _ = doctest.testmod(cifs, globs=env)
    assert failures == 0
