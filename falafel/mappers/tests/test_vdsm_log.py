import re
from falafel.mappers.vdsm_log import VDSMLog
from falafel.tests import context_wrap

LOG_REGEX = re.compile(r"Migration is stuck: Hasn't progressed in (\d)+(.)(\d)+ seconds. Aborting.")

VDSM_LOG = """
Thread-13::DEBUG::2016-07-13 04:45:39,371::fileSD::262::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '0+1 records in\n0+1 records out\n361 bytes (361 B) copied, 0.0012658 s, 285 kB/s\n'; <rc> = 0
Migration is stuck: Hasn't progressed in 300.093597889 seconds. Aborting.
jsonrpc.Executor-worker-2::INFO::2016-07-13 04:45:51,454::logUtils::44::dispatcher::(wrapper) Run and protect: repoStats(options=None)

"""


def test_vdsm_log():
    vdsm_log = VDSMLog.parse_context(context_wrap(VDSM_LOG))
    assert "Migration is stuck:" in vdsm_log
