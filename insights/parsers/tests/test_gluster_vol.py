import pytest
import doctest
from insights.parsers import ParseException, gluster_vol
from insights.tests import context_wrap
from insights.parsers.gluster_vol import GlusterVolInfo, GlusterVolStatus


# ---------------------------Gluster Vol Info Tests-----------------------------
TRACKING_VALID = """

Volume Name: test_vol
Type: Replicate
cluster.choose-local: off
network.remote-dio: enable
performance.low-prio-threads: 32
performance.io-cache: off
performance.read-ahead: off
performance.quick-read: off
nfs.disable: on
performance.client-io-threads: off
"""

TRACKING_INVALID = """ """

MULTIPLE_VOLUMES = """
Volume Name: test_vol
Type: Replicate
Volume ID: 2c32ed8d-5a07-4a76-a73a-123859556974
Status: Started
Snapshot Count: 0
Number of Bricks: 1 x 3 = 3
Transport-type: tcp
Bricks:
Brick1: 172.17.18.42:/home/brick
Brick2: 172.17.18.43:/home/brick
Brick3: 172.17.18.44:/home/brick
Options Reconfigured:
cluster.choose-local: off
user.cifs: off
features.shard: on
cluster.shd-wait-qlength: 10000
cluster.shd-max-threads: 8
cluster.locking-scheme: granular
cluster.data-self-heal-algorithm: full
cluster.server-quorum-type: server
cluster.quorum-type: auto
cluster.eager-lock: enable
network.remote-dio: enable
performance.low-prio-threads: 32
performance.io-cache: off
performance.read-ahead: off
performance.quick-read: off
transport.address-family: inet
nfs.disable: on
performance.client-io-threads: off

Volume Name: test_vol_2
Type: Replicate
Volume ID: dd821df9-ee2e-429c-98a0-81b1b794433d
Status: Started
Snapshot Count: 0
Number of Bricks: 1 x 3 = 3
Transport-type: tcp
Bricks:
Brick1: 172.17.18.42:/home/brick2
Brick2: 172.17.18.43:/home/brick2
Brick3: 172.17.18.44:/home/brick2
Options Reconfigured:
cluster.choose-local: off
user.cifs: off
features.shard: on
cluster.shd-wait-qlength: 10000
cluster.shd-max-threads: 8
cluster.locking-scheme: granular
cluster.data-self-heal-algorithm: full
cluster.server-quorum-type: server
cluster.quorum-type: auto
cluster.eager-lock: enable
network.remote-dio: enable
performance.low-prio-threads: 32
performance.io-cache: off
performance.read-ahead: off
performance.quick-read: off
transport.address-family: inet
nfs.disable: on
performance.client-io-threads: off
""".strip()


def test_gluster_vol_info_invalid():
    with pytest.raises(ParseException) as e:
        GlusterVolInfo(context_wrap(TRACKING_INVALID))
    assert "Unable to parse gluster volume options: []" in str(e)


def test_gluster_volume_options():
    parser_result = GlusterVolInfo(context_wrap(TRACKING_VALID))
    assert parser_result is not None

    data = parser_result.data["test_vol"]
    assert data['network.remote-dio'] == 'enable'
    assert data['cluster.choose-local'] == 'off'
    assert data['performance.client-io-threads'] == 'off'
    assert data['performance.quick-read'] == 'off'
    assert data['performance.low-prio-threads'] == '32'
    assert data['performance.io-cache'] == 'off'
    assert data['performance.read-ahead'] == 'off'
    assert data['nfs.disable'] == 'on'


def test_gluster_multiple_volume_options():
    parser_result = GlusterVolInfo(context_wrap(MULTIPLE_VOLUMES))
    assert parser_result is not None

    data = parser_result.data["test_vol"]
    assert data['network.remote-dio'] == 'enable'
    assert data['cluster.choose-local'] == 'off'
    assert data['performance.client-io-threads'] == 'off'
    assert data['performance.quick-read'] == 'off'
    assert data['performance.low-prio-threads'] == '32'
    assert data['performance.io-cache'] == 'off'
    assert data['performance.read-ahead'] == 'off'
    assert data['nfs.disable'] == 'on'

    data = parser_result.data["test_vol_2"]
    assert data['network.remote-dio'] == 'enable'
    assert data['cluster.choose-local'] == 'off'
    assert data['performance.client-io-threads'] == 'off'
    assert data['performance.quick-read'] == 'off'
    assert data['performance.low-prio-threads'] == '32'
    assert data['performance.io-cache'] == 'off'
    assert data['performance.read-ahead'] == 'off'
    assert data['nfs.disable'] == 'on'
# --------------------------------------END------------------------------------


# ---------------------------Gluster Vol Status Tests-----------------------------
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
    assert list(parser_data.keys()) == ["test_vol"]
    assert parser_data["test_vol"][0] == {
        'Gluster_process': 'Brick 172.17.18.42:/home/brick',
        'RDMA_Port': '0',
        'TCP_Port': '49152',
        'Pid': '26685',
        'Online': 'Y'
    }
    assert parser_data["test_vol"][1]["Online"] == 'Y'
    assert parser_data["test_vol"][1]["TCP_Port"] == '49152'
    assert parser_data["test_vol"][1]["Pid"] == '27094'
    assert parser_data["test_vol"][2] == {
            'Gluster_process': 'Brick 172.17.18.44:/home/brick',
            'RDMA_Port': '0',
            'TCP_Port': '49152',
            'Pid': '27060',
            'Online': 'Y'
    }
    assert parser_data["test_vol"][3] == {
            'Online': 'Y',
            'TCP_Port': 'N/A',
            'RDMA_Port': 'N/A',
            'Pid': '7805',
            'Gluster_process': 'Self-heal Daemon on localhost'
    }
    assert parser_data["test_vol"][4] == {
            'Online': 'Y',
            'TCP_Port': 'N/A',
            'RDMA_Port': 'N/A',
            'Pid': '33400',
            'Gluster_process': 'Self-heal Daemon on 172.17.18.44'
    }
    Self_heal_Daemon3_data = parser_data["test_vol"][5]
    assert Self_heal_Daemon3_data['RDMA_Port'] == 'N/A'


def test_multiple_valid():
    parser_result = GlusterVolStatus(context_wrap(VOL_STATUS_MULTIPLE_GOOD))
    parser_data = parser_result.data
    assert list(parser_data.keys()) == ["test_vol", "test_vol_2"]
    assert parser_data["test_vol_2"][0] == {
            'Gluster_process': 'Brick 172.17.18.42:/home/brick',
            'RDMA_Port': '0',
            'TCP_Port': '49152',
            'Pid': '6685',
            'Online': 'Y'
    }
    assert parser_data["test_vol_2"][1]["Online"] == 'Y'
    assert parser_data["test_vol_2"][1]["TCP_Port"] == '49152'
    assert parser_data["test_vol_2"][1]["Pid"] == '33094'
    assert parser_data["test_vol_2"][2] == {
            'Gluster_process': 'Brick 172.17.18.44:/home/brick',
            'RDMA_Port': '0',
            'TCP_Port': '49152',
            'Pid': '2060',
            'Online': 'Y'
    }
    assert parser_data["test_vol_2"][3] == {
            'Gluster_process': 'Self-heal Daemon on localhost',
            'RDMA_Port': 'N/A',
            'Pid': '7805',
            'TCP_Port': 'N/A',
            'Online': 'Y'}
# --------------------------------------END------------------------------------


def test_doc():
    INFO = TRACKING_VALID
    STATUS = VOL_STATUS_GOOD
    env = {
            "parser_result_v_info": GlusterVolInfo(context_wrap(INFO)),
            "parser_result_v_status": GlusterVolStatus(context_wrap(STATUS))
    }
    failed, total = doctest.testmod(gluster_vol, globs=env)
    assert failed == 0
