from falafel.tests import context_wrap
from falafel.mappers.host_vdsm_id import get_vdsm_id
UUID = 'F7D9D983-6233-45C2-A387-9B0C33CB1306'


def test_get_vdsm_id():
    expected = get_vdsm_id(context_wrap(UUID))
    assert UUID == expected
