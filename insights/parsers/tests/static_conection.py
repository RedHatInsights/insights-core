from insights.tests import context_wrap
from insights.parsers.static_connection import StaticConnectionShow

"""[root@rasrivas_rhel_redhat ~]# /usr/bin/nmcli connection show"""

"""
[
 {'NAME': 'enp0s3', 'UUID': '320d4923-c410-4b22-b7e9-afc5f794eecc', 'TYPE': 'ethernet', 'DEVICE': 'enp0s3'},
 {'NAME': 'virbr0', 'UUID': '7c7dec66-4a8c-4b49-834a-889194b3b83c', 'TYPE': 'bridge', 'DEVICE': 'virbr0'},
 {'NAME': 'test-net', 'UUID': 'f858b1cc-d149-4de0-93bc-b1826256847a', 'TYPE': 'ethernet', 'DEVICE': '--'}
]
"""


STATIC_CONNECTION_SHOW="""
NAME      UUID                                  TYPE      DEVICE 
enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3 
virbr0    7c7dec66-4a8c-4b49-834a-889194b3b83c  bridge    virbr0 
test-net-1  f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --
test-net-2 f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --

""".strip()

def test_static_connection():
    static_conn = StaticConnectionShow(context_wrap(STATIC_CONNECTION_SHOW))
    #disconnected_connection = static_conn.get_disconnected_connection

    assert static_conn[2]['DEVICE'] == "--"
    assert static_conn[2]['NAME'] == "test-net"
    #assert static_conn.disconnected_connection == ["test-net"]
    assert static_conn.get_disconnected_connection == ["test-net-1", "test-net-2"]
