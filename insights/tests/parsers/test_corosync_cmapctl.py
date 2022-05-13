import doctest
import pytest

from insights.tests import context_wrap
from insights.parsers import corosync_cmapctl, ParseException, SkipException
from insights.core.plugins import ContentException


COROSYNC_CONTENT_1 = """
config.totemconfig_reload_in_progress (u8) = 0
internal_configuration.service.0.name (str) = corosync_cmap
internal_configuration.service.0.ver (u32) = 0
internal_configuration.service.1.name (str) = corosync_cfg
internal_configuration.service.1.ver (u32) = 0
internal_configuration.service.2.name (str) = corosync_cpg
internal_configuration.service.2.ver (u32) = 0
internal_configuration.service.3.name (str) = corosync_quorum
internal_configuration.service.3.ver (u32) = 0
internal_configuration.service.4.name (str) = corosync_pload
internal_configuration.service.4.ver (u32) = 0
internal_configuration.service.5.name (str) = corosync_votequorum
internal_configuration.service.5.ver (u32) = 0
logging.logfile (str) = /var/log/cluster/corosync.log
logging.to_logfile (str) = yes
logging.to_syslog (str) = yes
nodelist.local_node_pos (u32) = 1
nodelist.node.0.nodeid (u32) = 1
""".strip()

COROSYNC_CONTENT_2 = """
stats.schedmiss.0.delay (flt) = 2023.957031
stats.schedmiss.0.timestamp (u64) = 5106558848098
stats.schedmiss.1.delay (flt) = 2023.436279
stats.schedmiss.1.timestamp (u64) = 5106556824141
stats.schedmiss.2.delay (flt) = 2030.076904
stats.schedmiss.2.timestamp (u64) = 5106554800704
stats.schedmiss.3.delay (flt) = 2022.936890
stats.schedmiss.3.timestamp (u64) = 5106552770627
stats.schedmiss.4.delay (flt) = 2024.749023
stats.schedmiss.4.timestamp (u64) = 5106550747691
stats.schedmiss.5.delay (flt) = 2021.841553
stats.schedmiss.5.timestamp (u64) = 5106548722942
stats.schedmiss.6.delay (flt) = 2024.137207
stats.schedmiss.6.timestamp (u64) = 5106546701100
stats.schedmiss.7.delay (flt) = 2021.287476
stats.schedmiss.7.timestamp (u64) = 5106544676963
stats.schedmiss.8.delay (flt) = 2025.073853
stats.schedmiss.8.timestamp (u64) = 5106542655675
stats.schedmiss.9.delay (flt) = 2473.122070
stats.schedmiss.9.timestamp (u64) = 5106540630601
""".strip()

COROSYNC_CONTENT_3 = """
""".strip()

COROSYNC_CONTENT_4 = """
corosync-cmapctl: invalid option -- 'C'
""".strip()

COROSYNC_CONTENT_5 = """
stats.schedmiss.7.timestamp (u64)5106544676963
stats.schedmiss.8.delay (flt) = 2025.073853
stats.schedmiss.8.timestamp (u64) = 5106542655675
stats.schedmiss.9.delay (flt) = 2473.122070
stats.schedmiss.9.timestamp (u64) = 5106540630601
""".strip()

COROSYNC_CONTENT_6 = """
config.totemconfig_reload_in_progress (u8) = 0
internal_configuration.service.0.name (str) = corosync_cmap
internal_configuration.service.0.ver (u32) = 0
internal_configuration.service.1.name (str) = corosync_cfg
internal_configuration.service.1.ver (u32) = 0
internal_configuration.service.2.name (str) = corosync_cpg
internal_configuration.service.2.ver (u32) = 0
internal_configuration.service.3.name (str) = corosync_quorum
internal_configuration.service.3.ver (u32) = 0
runtime.schedmiss.delay (flt) = 2282.403320
runtime.schedmiss.timestamp (u64) = 1589895874915
""".strip()


def test_corosync_doc_examples():
    env = {
        'corosync': corosync_cmapctl.CorosyncCmapctl(context_wrap(COROSYNC_CONTENT_1, path='corosync_cmpctl')),
    }
    failed, total = doctest.testmod(corosync_cmapctl, globs=env)
    assert failed == 0


def test_state_schemiss():
    corodata = corosync_cmapctl.CorosyncCmapctl(context_wrap(COROSYNC_CONTENT_2, path='corosync-cmapctl_-m_stats_stats.schedmiss'))
    assert 'stats.schedmiss.0.delay' in corodata
    assert corodata['stats.schedmiss.0.delay'] == '2023.957031'
    assert corodata['stats.schedmiss.0.timestamp'] == '5106558848098'
    assert len(corodata) == 20


def test_exception():
    with pytest.raises(SkipException):
        corosync_cmapctl.CorosyncCmapctl(context_wrap(COROSYNC_CONTENT_3, path="corosync_cmpctl"))
    with pytest.raises(ContentException):
        corosync_cmapctl.CorosyncCmapctl(context_wrap(COROSYNC_CONTENT_4, path="corosync_cmpctl_-C"))
    with pytest.raises(ParseException):
        corosync_cmapctl.CorosyncCmapctl(context_wrap(COROSYNC_CONTENT_5, path="corosync_cmpctl"))


def test_runtime_schemiss():
    corodata = corosync_cmapctl.CorosyncCmapctl(context_wrap(COROSYNC_CONTENT_6, path='corosync-cmapctl'))
    assert "runtime.schedmiss.delay" in corodata
    assert corodata['runtime.schedmiss.delay'] == '2282.403320'
    assert "runtime.schedmiss.timestamp" in corodata
    assert corodata['runtime.schedmiss.timestamp'] == '1589895874915'
