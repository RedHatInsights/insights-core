from insights.parsers.nmcli import NmcliConnShow
from insights.specs.datasources.nmcli import nmcli_conn_show_uuids
from insights.tests import context_wrap


NMCLI_CONN_SHOW = '''
NAME                UUID                                  TYPE      DEVICE
Wired connection 2  5fb06bd0-b09a-4573-b393-ffffffffffff  ethernet  enp0s20f0u5c2
lo                  10f69a0f-0bb0-409f-831f-dddddddddddd  loopback  lo
Wired connection 1  9dc5d4c5-71ae-44fb-804a-cccccccccccc  ethernet  --
enp0s29f2           bb30e099-8220-3eba-45f1-aaaaaaaaaaaa  ethernet  --
'''.strip()


def test_nmcli_conn_show_uuids():
    nmcli_conn_show = NmcliConnShow(context_wrap(NMCLI_CONN_SHOW))
    broker = {NmcliConnShow: nmcli_conn_show}
    result = nmcli_conn_show_uuids(broker)
    assert result == ['5fb06bd0-b09a-4573-b393-ffffffffffff', '10f69a0f-0bb0-409f-831f-dddddddddddd', '9dc5d4c5-71ae-44fb-804a-cccccccccccc', 'bb30e099-8220-3eba-45f1-aaaaaaaaaaaa']
