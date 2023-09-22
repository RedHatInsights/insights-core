import doctest
from insights.parsers import pcp_openmetrics_log
from insights.tests import context_wrap


PCP_OPENMETRICS_LOG = """
[Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store 55% {:
[Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store }:
[Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store 95% {:
[Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store }:
[Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store };:
""".strip()


def test_pcp_openmetrics_log():
    log = pcp_openmetrics_log.PcpOpenmetricsLog(context_wrap(PCP_OPENMETRICS_LOG))
    assert "Error: cannot parse/store" in log
    assert len(log.get('pmdaopenmetrics')) == 5


def test_documentation():
    failed_count, tests = doctest.testmod(
        pcp_openmetrics_log,
        globs={'log': pcp_openmetrics_log.PcpOpenmetricsLog(context_wrap(PCP_OPENMETRICS_LOG))}
    )
    assert failed_count == 0
