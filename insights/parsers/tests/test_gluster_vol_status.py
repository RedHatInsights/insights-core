import pytest
from insights.parsers import ParseException
from insights.tests import context_wrap
from insights.parsers.gluster_vol import GlusterVolStatus

VOL_STATUS_BAD = """
""".strip()

VOL_STATUS_GOOD = """
Status of volume: test_vol
Gluster process                             TCP Port  RDMA Port  Online  Pid
------------------------------------------------------------------------------
Brick 172.17.18.42:/home/brick              49152     0          Y       26685
Brick 172.17.18.43:/home/brick              49152     0          Y       27094
Brick 172.17.18.44:/home/brick              49152     0          Y       27060
Self-heal Daemon on localhost               N/A       N/A        Y       7805
Self-heal Daemon on 172.17.18.44            N/A       N/A        Y       33400
Self-heal Daemon on 172.17.18.43            N/A       N/A        Y       33680

Task Status of Volume test_vol
------------------------------------------------------------------------------
There are no active volume tasks
""".strip()

VOL_STATUS_MULTIPLE_GOOD = """
Status of volume: test_vol
Gluster process                             TCP Port  RDMA Port  Online  Pid
------------------------------------------------------------------------------
Brick 172.17.18.42:/home/brick              49152     0          Y       26685
Brick 172.17.18.43:/home/brick              49152     0          Y       27094
Brick 172.17.18.44:/home/brick              49152     0          Y       27060
Self-heal Daemon on localhost               N/A       N/A        Y       7805
Self-heal Daemon on 172.17.18.44            N/A       N/A        Y       33400
Self-heal Daemon on 172.17.18.43            N/A       N/A        Y       33680

Task Status of Volume test_vol
------------------------------------------------------------------------------
There are no active volume tasks


Status of volume: test_vol_2
Gluster process                             TCP Port  RDMA Port  Online  Pid
------------------------------------------------------------------------------
Brick 172.17.18.42:/home/brick              49152     0          Y       6685
Brick 172.17.18.43:/home/brick              49152     0          Y       33094
Brick 172.17.18.44:/home/brick              49152     0          Y       2060
Self-heal Daemon on localhost               N/A       N/A        Y       7805
Self-heal Daemon on 172.17.18.44            N/A       N/A        Y       33400
Self-heal Daemon on 172.17.18.43            N/A       N/A        Y       33680

Task Status of Volume test_vol
------------------------------------------------------------------------------
There are no active volume tasks

""".strip()


def test_invalid():
    with pytest.raises(ParseException) as e:
        GlusterVolStatus(context_wrap(VOL_STATUS_BAD))
    assert "Unable to parse gluster volume status: []" in str(e)


def test_valid():
    parser_result = GlusterVolStatus(context_wrap(VOL_STATUS_GOOD))
    parser_data = parser_result.data
    assert list(parser_data.keys() )== ["test_vol"]
    assert parser_data["test_vol"][0] == {
            'Gluster_process': 'Brick 172.17.18.42:/home/brick',
            'RDMA_Port': '0',
            'IP': '172.17.18.42',
            'TCP_Port': '49152',
            'Pid': '26685',
            'Online': 'Y',
            'Directory': '/home/brick'
            }
    assert parser_data["test_vol"][1]["Online"] == 'Y'
    assert parser_data["test_vol"][1]["IP"] == '172.17.18.43'
    assert parser_data["test_vol"][1]["TCP_Port"] == '49152'
    assert parser_data["test_vol"][1]["Pid"] == '27094'
    assert parser_data["test_vol"][1]["Directory"] == '/home/brick'
    assert parser_data["test_vol"][2] == {
            'Gluster_process': 'Brick 172.17.18.44:/home/brick',
            'RDMA_Port': '0',
            'IP': '172.17.18.44',
            'TCP_Port': '49152',
            'Pid': '27060',
            'Online': 'Y',
            'Directory': '/home/brick'
            }
    assert parser_data["test_vol"][3] == {
            'Gluster_process': 'Self-heal Daemon on localhost',
            'RDMA_Port': 'N/A',
            'Host': 'localhost',
            'Pid': '7805',
            'TCP_Port': 'N/A',
            'Online': 'Y'
            }
    assert parser_data["test_vol"][4] == {
            'Gluster_process': 'Self-heal Daemon on 172.17.18.44',
            'RDMA_Port': 'N/A',
            'Host': '172.17.18.44',
            'Pid': '33400',
            'TCP_Port': 'N/A',
            'Online': 'Y'
            }
    Self_heal_Daemon3_data = parser_data["test_vol"][5]
    assert Self_heal_Daemon3_data['RDMA_Port'] == 'N/A'
    assert Self_heal_Daemon3_data["Host"] == '172.17.18.43'


def test_multiple_valid():
    parser_result = GlusterVolStatus(context_wrap(VOL_STATUS_MULTIPLE_GOOD))
    parser_data = parser_result.data
    assert list(parser_data.keys()) == ["test_vol", "test_vol_2"]
    assert parser_data["test_vol_2"][0] == {
            'Gluster_process': 'Brick 172.17.18.42:/home/brick',
            'RDMA_Port': '0',
            'IP': '172.17.18.42',
            'TCP_Port': '49152',
            'Pid': '6685',
            'Online': 'Y',
            'Directory': '/home/brick'
            }
    assert parser_data["test_vol_2"][1]["Online"] == 'Y'
    assert parser_data["test_vol_2"][1]["IP"] == '172.17.18.43'
    assert parser_data["test_vol_2"][1]["TCP_Port"] == '49152'
    assert parser_data["test_vol_2"][1]["Pid"] == '33094'
    assert parser_data["test_vol_2"][1]["Directory"] == '/home/brick'
    assert parser_data["test_vol_2"][2] == {
            'Gluster_process': 'Brick 172.17.18.44:/home/brick',
            'RDMA_Port': '0',
            'IP': '172.17.18.44',
            'TCP_Port': '49152',
            'Pid': '2060',
            'Online': 'Y',
            'Directory': '/home/brick'
            }
    assert parser_data["test_vol_2"][3] == {
            'Gluster_process': 'Self-heal Daemon on localhost',
            'RDMA_Port': 'N/A',
            'Host': 'localhost',
            'Pid': '7805',
            'TCP_Port': 'N/A',
            'Online': 'Y'}
