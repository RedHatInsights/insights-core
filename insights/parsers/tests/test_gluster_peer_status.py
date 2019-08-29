import doctest
import pytest
from insights.parsers import gluster_peer_status, SkipException
from insights.tests import context_wrap

OUTPUT = """
Number of Peers: 1

Hostname: versegluster1.verse.loc
Uuid: 86c0266b-c78c-4d0c-afe7-953dec143530
State: Peer in Cluster (Connected)
""".strip()

OUTPUT_1 = """
Number of Peers: 3

Hostname: versegluster1.verse.loc
Uuid: 86c0266b-c78c-4d0c-afe7-953dec143530
State: Peer in Cluster (Connected)

Hostname: 10.30.32.16
Uuid: 3b4673e3-5e95-4c02-b9bb-2823483e067b
State: Peer in Cluster (Connected)

Hostname: 10.30.32.20
Uuid: 4673e3-5e95-4c02-b9bb-2823483e067bb3
State: Peer in Cluster (Disconnected)
""".strip()


def test_output():
    output = gluster_peer_status.GlusterPeerStatus(context_wrap(OUTPUT_1))
    assert output.status['peers'] == len(output.status.get('hosts', []))
    assert output.status.get('hosts', []) == [
        {'Hostname': 'versegluster1.verse.loc', 'State': 'Peer in Cluster (Connected)', 'Uuid': '86c0266b-c78c-4d0c-afe7-953dec143530'},
        {'Hostname': '10.30.32.16', 'State': 'Peer in Cluster (Connected)', 'Uuid': '3b4673e3-5e95-4c02-b9bb-2823483e067b'},
        {'Hostname': '10.30.32.20', 'State': 'Peer in Cluster (Disconnected)', 'Uuid': '4673e3-5e95-4c02-b9bb-2823483e067bb3'}
    ]


def test_blank_output():
    with pytest.raises(SkipException) as e:
        gluster_peer_status.GlusterPeerStatus(context_wrap(""))
    assert "No data." in str(e)


def test_documentation():
    failed_count, tests = doctest.testmod(
        gluster_peer_status,
        globs={'output': gluster_peer_status.GlusterPeerStatus(context_wrap(OUTPUT))}
    )
    assert failed_count == 0
