from insights.parsers import crictl_logs
from insights.parsers.crictl_logs import CrictlLogs
from insights.tests import context_wrap
import doctest

CRICTL_LOGS = """
2021-12-21T11:12:45.854971114+01:00 Successfully copied files in /usr/src/multus-cni/rhel7/bin/ to /host/opt/cni/bin/
2021-12-21T11:12:45.995998017+01:00 2021-12-21T10:12:45+00:00 WARN: {unknown parameter "-"}
2021-12-21T11:12:46.008998978+01:00 2021-12-21T10:12:46+00:00 Entrypoint skipped copying Multus binary.
2021-12-21T11:12:46.081427544+01:00 2021-12-21T10:12:46+00:00 Attempting to find master plugin configuration, attempt 0
""".strip()


def test_crictl_logs():
    logs = CrictlLogs(context_wrap(CRICTL_LOGS))
    test_1 = logs.get('skipped copying Multus binary')
    assert 1 == len(test_1)
    test_2 = logs.get('Attempting to find master plugin configuration')
    assert 1 == len(test_2)
    assert test_2[0]['raw_message'] == '2021-12-21T11:12:46.081427544+01:00 2021-12-21T10:12:46+00:00 Attempting to find master plugin configuration, attempt 0'


def test_crictl_logs_documentation():
    failed_count, tests = doctest.testmod(
        crictl_logs,
        globs={'logs': CrictlLogs(context_wrap(CRICTL_LOGS))}
    )
    assert failed_count == 0
