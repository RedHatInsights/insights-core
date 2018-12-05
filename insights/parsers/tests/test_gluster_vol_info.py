import pytest
from insights.parsers import ParseException
from insights.tests import context_wrap
from insights.parsers.gluster_vol import GlusterVolInfo


TRACKING_VALID = """

Volume Name: test_vol
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


def test_invalid():
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
