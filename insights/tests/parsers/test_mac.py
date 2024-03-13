import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import mac
from insights.tests import context_wrap


MAC_OK = """
00:5b:ea:09:00:00
""".strip()

MAC_NG = """
h0:5b:ea:09:00:00
""".strip()


def test_mac_address():
    ret = mac.MacAddress(context_wrap(MAC_OK))
    assert ret.address == '00:5b:ea:09:00:00'

    with pytest.raises(SkipComponent):
        mac.MacAddress(context_wrap(MAC_NG))


def test_mac_doc():
    env = {
            'mac_addr': mac.MacAddress(context_wrap(MAC_OK)),
          }
    failed, total = doctest.testmod(mac, globs=env)
    assert failed == 0
