from insights.tests import context_wrap
from insights.parsers.nmcli import NmcliDevShow, NmcliDevShowSos
from insights.parsers.nmcli import NmcliConnShow
from insights.parsers import nmcli, SkipException
import doctest
import pytest

NMCLI_SHOW = """
GENERAL.DEVICE:                         em3
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         B8:2A:72:DE:F8:B9
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     em3
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/1
WIRED-PROPERTIES.CARRIER:               on
IP4.ADDRESS[1]:                         10.16.184.98/22
IP4.GATEWAY:                             10.16.187.254
IP4.DNS[1]:                             10.16.36.29
IP4.DNS[2]:                             10.11.5.19
IP4.DNS[3]:                             10.5.30.160
IP4.DOMAIN[1]:                          khw.lab.eng.bos.example.com
IP6.ADDRESS[1]:                         2620:52:0:10bb:ba2a:72ff:fede:f8b9/64
IP6.ADDRESS[2]:                         fe80::ba2a:72ff:fede:f8b9/64
IP6.GATEWAY:                            fe80:52:0:10bb::fc
IP6.ROUTE[1]:                           dst = 2620:52:0:10bb::/64, nh = ::, mt = 100

GENERAL.DEVICE:                         em1
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         B8:2A:72:DE:F8:BB
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 connected
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
WIRED-PROPERTIES.CARRIER:               off

GENERAL.DEVICE:                         em2
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         B8:AA:BB:DE:F8:BC
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
WIRED-PROPERTIES.CARRIER:               off
"""

NMCLI_SHOW_SOS = """
GENERAL.DEVICE:                         em3
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         B8:2A:72:DE:F8:B9
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     em3
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/1
WIRED-PROPERTIES.CARRIER:               on
IP4.ADDRESS[1]:                         10.16.184.98/22
IP4.GATEWAY:                             10.16.187.254
IP4.DNS[1]:                             10.16.36.29
IP4.DNS[2]:                             10.11.5.19
IP4.DNS[3]:                             10.5.30.160
IP4.DOMAIN[1]:                          khw.lab.eng.bos.example.com
IP6.ADDRESS[1]:                         2620:52:0:10bb:ba2a:72ff:fede:f8b9/64
IP6.ADDRESS[2]:                         fe80::ba2a:72ff:fede:f8b9/64
IP6.GATEWAY:                            fe80:52:0:10bb::fc
IP6.ROUTE[1]:                           dst = 2620:52:0:10bb::/64, nh = ::, mt = 100
""".strip()

NMCLI_SHOW_ERROR = """
Error: Option '-l' is unknown, try 'nmcli -help'.
"""

NMCLI_SHOW_ERROR_2 = """
Error: Option '-l' is unknown, try 'nmcli -help'.
Warning: nmcli (1.0.0) and NetworkManager (1.0.6) versions don't match. Use --nocheck to suppress the warning.
"""

STATIC_CONNECTION_SHOW_1 = """
NAME      UUID                                  TYPE      DEVICE
enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3
virbr0    7c7dec66-4a8c-4b49-834a-889194b3b83c  bridge    virbr0
test-net-1  f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --
""".strip()

STATIC_CONNECTION_SHOW_2 = """
NAME      UUID                                  TYPE      DEVICE
enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3
virbr0    7c7dec66-4a8c-4b49-834a-889194b3b83c  bridge    virbr0
test-net-1  f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --
test-net-2 f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --
""".strip()

STATIC_CONNECTION_SHOW_3 = """
Warning: nmcli (1.0.0) and NetworkManager (1.0.6) versions don't match. Use --nocheck to suppress the warning.
NAME           UUID                                  TYPE            DEVICE
enp0s8         00cb8299-feb9-55b6-a378-3fdc720e0bc6  802-3-ethernet  --
enp0s3         bfb4760c-96ce-4a29-9f2e-7427051da943  802-3-ethernet  enp0s3"
""".strip()

STATIC_CONNECTION_SHOW_4 = """
Warning: nmcli (1.0.0) and NetworkManager (1.0.6) versions don't match. Use --nocheck to suppress the warning.
NAME                UUID                                  TYPE      DEVICE
System eth0         5fb06bd0-0bb0-7ffb-45f1-d6edd65f3e03  ethernet  eth0
Wired connection 1  ba12c52b-cd0e-39a0-a95b-643a0859664e  ethernet  eth1
Wired connection 2  fa8d308c-2e00-336c-9dee-2def12e240c7  ethernet  eth2
team0               bf000427-d9f1-432f-819d-257edb86c6fb  team      team0
""".strip()

NMCLI_DEV_SHOW = """
TextFileProvider("'/tmp/insights-fcct09p0/insights-rhel7-box-20191016082653/insights_commands/nmcli_dev_show'")
GENERAL.DEVICE:                         br0
GENERAL.TYPE:                           bridge
GENERAL.HWADDR:                         7A:C3:4C:23:65:8A
GENERAL.MTU:                            1450
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     br0
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/1
IP4.GATEWAY:
IP6.ADDRESS[1]:                         fe80::78c3:4cff:fe23:658a/64
IP6.GATEWAY:

GENERAL.DEVICE:                         enp0s3
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         08:00:27:4A:C5:EF
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     enp0s3
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/0
WIRED-PROPERTIES.CARRIER:               on
IP4.ADDRESS[1]:                         10.0.2.15/24
IP4.GATEWAY:                            10.0.2.2
IP4.DNS[1]:                             10.0.2.3
IP4.DOMAIN[1]:                          redhat.com
IP6.ADDRESS[1]:                         fe80::a00:27ff:fe4a:c5ef/64
IP6.GATEWAY:

GENERAL.DEVICE:                         vxlan10
GENERAL.TYPE:                           vxlan
GENERAL.HWADDR:                         7A:C3:4C:23:65:8A
GENERAL.MTU:                            1450
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     vxlan10
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/2
IP4.GATEWAY:
IP6.GATEWAY:

GENERAL.DEVICE:                         enp0s8
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         08:00:27:45:74:6B
GENERAL.MTU:                            1500
GENERAL.STATE:                          30 (disconnected)
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
WIRED-PROPERTIES.CARRIER:               on

GENERAL.DEVICE:                         enp0s9
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         08:00:27:F2:32:1E
GENERAL.MTU:                            1500
GENERAL.STATE:                          30 (disconnected)
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
WIRED-PROPERTIES.CARRIER:               on

GENERAL.DEVICE:                         lo
GENERAL.TYPE:                           loopback
GENERAL.HWADDR:                         00:00:00:00:00:00
GENERAL.MTU:                            65536
GENERAL.STATE:                          10 (unmanaged)
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
IP4.ADDRESS[1]:                         127.0.0.1/8
IP4.GATEWAY:
IP6.ADDRESS[1]:                         ::1/128
IP6.GATEWAY:
""".strip()


def test_nmcli():
    nmcli_obj = NmcliDevShow(context_wrap(NMCLI_SHOW))
    con_dev = nmcli_obj.connected_devices
    assert sorted(con_dev) == sorted(['em1', 'em3', 'em2'])
    assert nmcli_obj['em3']['IP4_GATEWAY'] == "10.16.187.254"
    assert nmcli_obj['em3']['IP4_DNS1'] == "10.16.36.29"
    assert nmcli_obj['em3']['IP6_ROUTE1'] == "dst = 2620:52:0:10bb::/64, nh = ::, mt = 100"
    assert nmcli_obj['em1']['STATE'] == "connected"
    assert nmcli_obj['em1']['CON-PATH'] == "--"
    assert nmcli_obj['em3']['IP6_ADDRESS1'] == "2620:52:0:10bb:ba2a:72ff:fede:f8b9/64"
    assert nmcli_obj['em3']['IP6_ADDRESS2'] == "fe80::ba2a:72ff:fede:f8b9/64"
    assert nmcli_obj['em3']['CON-PATH'] == "/org/freedesktop/NetworkManager/ActiveConnection/1"
    assert len(nmcli_obj['em3']) == 17
    assert len(nmcli_obj['em1']) == 7
    nmcli_obj = NmcliDevShow(context_wrap(NMCLI_DEV_SHOW))
    assert 'IP6_GATEWAY' not in nmcli_obj['lo']
    assert 'IP6_ADDRESS1' in nmcli_obj['lo']
    assert nmcli_obj['lo']['IP6_ADDRESS1'] == '::1/128'
    assert nmcli_obj.data is not None


def test_nmcli_sos():
    nmcli_obj = NmcliDevShowSos(context_wrap(NMCLI_SHOW_SOS))
    con_dev = nmcli_obj.connected_devices
    assert sorted(con_dev) == sorted(['em3'])
    assert nmcli_obj['em3']['IP4_GATEWAY'] == "10.16.187.254"
    assert nmcli_obj['em3']['IP4_DNS1'] == "10.16.36.29"
    assert nmcli_obj['em3']['IP6_ROUTE1'] == "dst = 2620:52:0:10bb::/64, nh = ::, mt = 100"
    assert nmcli_obj['em3']['IP6_ADDRESS1'] == "2620:52:0:10bb:ba2a:72ff:fede:f8b9/64"
    assert nmcli_obj['em3']['IP6_ADDRESS2'] == "fe80::ba2a:72ff:fede:f8b9/64"
    assert nmcli_obj['em3']['CON-PATH'] == "/org/freedesktop/NetworkManager/ActiveConnection/1"
    assert len(nmcli_obj['em3']) == 17


def test_static_connection_test_1():
    static_conn = NmcliConnShow(context_wrap(STATIC_CONNECTION_SHOW_1))
    assert static_conn.data[0] == {'NAME': 'enp0s3', 'UUID': '320d4923-c410-4b22-b7e9-afc5f794eecc', 'TYPE': 'ethernet', 'DEVICE': 'enp0s3'}
    assert static_conn.disconnected_connection == ["test-net-1"]


def test_static_connection_test_2():
    static_conn = NmcliConnShow(context_wrap(STATIC_CONNECTION_SHOW_2))
    assert static_conn.disconnected_connection == ["test-net-1", "test-net-2"]


def test_static_connection_test_3():
    static_conn = NmcliConnShow(context_wrap(STATIC_CONNECTION_SHOW_3))
    assert static_conn.disconnected_connection == ["enp0s8"]


def test_static_connection_test_4():
    static_conn = NmcliConnShow(context_wrap(STATIC_CONNECTION_SHOW_4))
    assert static_conn.data[1] == {'NAME': 'Wired connection 1', 'UUID': 'ba12c52b-cd0e-39a0-a95b-643a0859664e', 'TYPE': 'ethernet', 'DEVICE': 'eth1'}
    assert static_conn.data[3] == {'NAME': 'team0', 'UUID': 'bf000427-d9f1-432f-819d-257edb86c6fb', 'TYPE': 'team', 'DEVICE': 'team0'}


def test_nmcli_dev_show_ab():
    with pytest.raises(SkipException):
        NmcliDevShow(context_wrap(''))

    with pytest.raises(SkipException):
        NmcliDevShow(context_wrap('GENERAL.TYPE: ethernet'))

    with pytest.raises(SkipException):
        NmcliDevShow(context_wrap('Error'))


def test_nmcli_doc_examples():
    env = {
        'nmcli_obj': NmcliDevShow(context_wrap(NMCLI_SHOW)),
        'nmcli_obj_sos': NmcliDevShowSos(context_wrap(NMCLI_SHOW_SOS)),
        'static_conn': NmcliConnShow(context_wrap(STATIC_CONNECTION_SHOW_1)),
    }
    failed, total = doctest.testmod(nmcli, globs=env)
    assert failed == 0


def test_nmcli_exceptions():
    with pytest.raises(SkipException) as exc:
        nmcli_obj = NmcliConnShow(context_wrap(NMCLI_SHOW_ERROR))
        nmcli_obj = NmcliConnShow(context_wrap(NMCLI_SHOW_ERROR_2))
        assert nmcli_obj is None
    assert 'Invalid Contents!' in str(exc)
