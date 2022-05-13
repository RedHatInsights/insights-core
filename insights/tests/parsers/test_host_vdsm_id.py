from insights.tests import context_wrap
from insights.parsers.host_vdsm_id import VDSMId

UUID = 'F7D9D983-6233-45C2-A387-9B0C33CB1306'

UUID_CONTENT = """
# VDSM UUID info
#
F7D9D983-6233-45C2-A387-9B0C33CB1306
""".strip()


def test_get_vdsm_id():
    expected = VDSMId(context_wrap(UUID_CONTENT))
    assert UUID == expected.uuid
