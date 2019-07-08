from insights.tests import context_wrap
from insights.combiners.nmcli_dev_show import AllNmcliDevShow
from insights.combiners import nmcli_dev_show
from insights.parsers.nmcli import NmcliDevShow
import doctest

NMCLI_SHOW1 = """
GENERAL.DEVICE:                         eth0
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         00:1A:4A:16:02:E0
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     System eth0
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/1
WIRED-PROPERTIES.CARRIER:               on
IP4.ADDRESS[1]:                         10.72.37.85/23
IP4.GATEWAY:                            10.72.37.254
IP4.ROUTE[1]:                           dst = 0.0.0.0/0, nh = 10.72.37.254, mt = 100
IP4.ROUTE[2]:                           dst = 10.72.36.0/23, nh = 0.0.0.0, mt = 100
IP4.DNS[1]:                             10.72.17.5
IP4.DOMAIN[1]:                          gsslab.pek2.redhat.com
IP6.ADDRESS[1]:                         2620:52:0:4824:21a:4aff:fe16:2e0/64
IP6.ADDRESS[2]:                         fe80::21a:4aff:fe16:2e0/64
IP6.GATEWAY:                            fe80:52:0:4824::1fe
IP6.ROUTE[1]:                           dst = ff00::/8, nh = ::, mt = 256, table=255
IP6.ROUTE[2]:                           dst = fe80::/64, nh = ::, mt = 256
IP6.ROUTE[3]:                           dst = ::/0, nh = fe80:52:0:4824::1fe, mt = 1024
IP6.ROUTE[4]:                           dst = 2620:52:0:4824::/64, nh = ::, mt = 256

GENERAL.DEVICE:                         lo
GENERAL.TYPE:                           loopback
GENERAL.HWADDR:                         00:00:00:00:00:00
GENERAL.MTU:                            65536
GENERAL.STATE:                          10 (unmanaged)
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
IP4.ADDRESS[1]:                         127.0.0.1/8
IP4.GATEWAY:                            --
IP6.ADDRESS[1]:                         ::1/128
IP6.GATEWAY:                            --
""".strip()

NMCLI_SHOW2 = """
GENERAL.DEVICE:                         eth0
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         00:1A:4A:16:02:E0
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     System eth0
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/1
WIRED-PROPERTIES.CARRIER:               on
IP4.ADDRESS[1]:                         10.72.37.85/23
IP4.GATEWAY:                            10.72.37.254
IP4.ROUTE[1]:                           dst = 0.0.0.0/0, nh = 10.72.37.254, mt = 100
IP4.ROUTE[2]:                           dst = 10.72.36.0/23, nh = 0.0.0.0, mt = 100
IP4.DNS[1]:                             10.72.17.5
IP4.DOMAIN[1]:                          gsslab.pek2.redhat.com
IP6.ADDRESS[1]:                         2620:52:0:4824:21a:4aff:fe16:2e0/64
IP6.ADDRESS[2]:                         fe80::21a:4aff:fe16:2e0/64
IP6.GATEWAY:                            fe80:52:0:4824::1fe
IP6.ROUTE[1]:                           dst = ff00::/8, nh = ::, mt = 256, table=255
IP6.ROUTE[2]:                           dst = fe80::/64, nh = ::, mt = 256
IP6.ROUTE[3]:                           dst = ::/0, nh = fe80:52:0:4824::1fe, mt = 1024
IP6.ROUTE[4]:                           dst = 2620:52:0:4824::/64, nh = ::, mt = 256
""".strip()

NMCLI_SHOW3 = """
GENERAL.DEVICE:                         lo
GENERAL.TYPE:                           loopback
GENERAL.HWADDR:                         00:00:00:00:00:00
GENERAL.MTU:                            65536
GENERAL.STATE:                          10 (unmanaged)
GENERAL.CONNECTION:                     --
GENERAL.CON-PATH:                       --
IP4.ADDRESS[1]:                         127.0.0.1/8
IP4.GATEWAY:                            --
IP6.ADDRESS[1]:                         ::1/128
IP6.GATEWAY:                            --
""".strip()


def test_allnmcli1():
    nmcli_obj = NmcliDevShow(context_wrap(NMCLI_SHOW1))
    allnmcli_obj = AllNmcliDevShow(nmcli_obj, None)
    con_dev = allnmcli_obj.connected_devices
    assert sorted(con_dev) == sorted(['eth0'])
    assert allnmcli_obj['eth0']['IP4_GATEWAY'] == "10.72.37.254"
    assert allnmcli_obj['eth0']['IP4_DNS1'] == "10.72.17.5"
    assert allnmcli_obj['eth0']['STATE'] == "connected"
    assert allnmcli_obj['eth0']['CON-PATH'] == "/org/freedesktop/NetworkManager/ActiveConnection/1"
    assert len(allnmcli_obj['lo']) == 10


def test_allnmcli2():
    nmcli_obj1 = NmcliDevShow(context_wrap(NMCLI_SHOW2))
    nmcli_obj2 = NmcliDevShow(context_wrap(NMCLI_SHOW3))
    allnmcli_obj = AllNmcliDevShow(None, [nmcli_obj1, nmcli_obj2])
    con_dev = allnmcli_obj.connected_devices
    assert sorted(con_dev) == sorted(['eth0'])
    assert allnmcli_obj['eth0']['IP4_GATEWAY'] == "10.72.37.254"
    assert allnmcli_obj['eth0']['IP4_DNS1'] == "10.72.17.5"
    assert allnmcli_obj['eth0']['STATE'] == "connected"
    assert allnmcli_obj['eth0']['CON-PATH'] == "/org/freedesktop/NetworkManager/ActiveConnection/1"
    assert len(allnmcli_obj['lo']) == 10


def test_doc_examples():
    env = {
            'allnmclidevshow': AllNmcliDevShow(NmcliDevShow(context_wrap(NMCLI_SHOW1)), None),
          }
    failed, total = doctest.testmod(nmcli_dev_show, globs=env)
    assert failed == 0
