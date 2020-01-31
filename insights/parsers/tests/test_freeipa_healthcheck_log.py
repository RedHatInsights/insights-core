import doctest
from insights.parsers import freeipa_healthcheck_log
from insights.parsers.freeipa_healthcheck_log import FreeIPAHealthCheckLog
from insights.tests import context_wrap

LONG_FREEIPA_HEALTHCHECK_LOG_OK = """
[{"source": "ipahealthcheck.ipa.roles", "check": "IPACRLManagerCheck",
"result": "SUCCESS", "uuid": "1f4177a4-0ddb-4e4d-8258-a5cd5f4638fc",
"when": "20191203122317Z", "duration": "0.002254",
"kw": {"key": "crl_manager", "crlgen_enabled": true}}]
""".strip()

LONG_FREEIPA_HEALTHCHECK_LOG_FAILURES = """
[{"source": "ipahealthcheck.system.filesystemspace",
"check": "FileSystemSpaceCheck",
"result": "ERROR", "uuid": "90ed8765-6ad7-425c-abbd-b07a652649cb",
"when": "20191203122221Z", "duration": "0.000474", "kw": {
"msg": "/var/log/audit/: free space under threshold: 14 MiB < 512 MiB",
"store": "/var/log/audit/", "free_space": 14, "threshold": 512}}]
""".strip()

FREEIPA_HEALTHCHECK_LOG_DOCS_EXAMPLE = '''
    [
      {
        "source": "ipahealthcheck.ipa.roles",
        "check": "IPACRLManagerCheck",
        "result": "SUCCESS",
        "uuid": "1f4177a4-0ddb-4e4d-8258-a5cd5f4638fc",
        "when": "20191203122317Z",
        "duration": "0.002254",
        "kw": {
          "key": "crl_manager",
          "crlgen_enabled": true
        }
      },
      {
        "source": "ipahealthcheck.ipa.roles",
        "check": "IPARenewalMasterCheck",
        "result": "SUCCESS",
        "uuid": "1feb7f99-2e98-4e37-bb52-686896972022",
        "when": "20191203122317Z",
        "duration": "0.018330",
        "kw": {
          "key": "renewal_master",
          "master": true
        }
      },
      {
        "source": "ipahealthcheck.system.filesystemspace",
        "check": "FileSystemSpaceCheck",
        "result": "ERROR",
        "uuid": "90ed8765-6ad7-425c-abbd-b07a652649cb",
        "when": "20191203122221Z",
        "duration": "0.000474",
        "kw": {
          "msg": "/var/log/audit/: free space under threshold: 14 MiB < 512 MiB",
          "store": "/var/log/audit/",
          "free_space": 14,
          "threshold": 512
         }
       }
    ]
'''.strip()


FREEIPA_HEALTHCHECK_LOG_OK = "".join(LONG_FREEIPA_HEALTHCHECK_LOG_OK.splitlines())
FREEIPA_HEALTHCHECK_LOG_FAILURES = "".join(LONG_FREEIPA_HEALTHCHECK_LOG_FAILURES.splitlines())


def test_freeipa_healthcheck_log_ok():
    log_obj = FreeIPAHealthCheckLog(context_wrap(FREEIPA_HEALTHCHECK_LOG_OK))
    assert len(log_obj.issues) == 0


def test_freeipa_healthcheck_log_not_ok():
    log_obj = FreeIPAHealthCheckLog(context_wrap(FREEIPA_HEALTHCHECK_LOG_FAILURES))
    assert len(log_obj.issues) > 0
    for issue in log_obj.issues:
        assert issue['check'] == 'FileSystemSpaceCheck'
        assert issue['source'] == 'ipahealthcheck.system.filesystemspace'


def test_freeipa_healthcheck_get_results_ok():
    log_obj = FreeIPAHealthCheckLog(context_wrap(FREEIPA_HEALTHCHECK_LOG_OK))
    results = log_obj.get_results('ipahealthcheck.system.filesystemspace', 'FileSystemSpaceCheck')
    assert len(results) == 0


def test_freeipa_healthcheck_get_results_not_ok():
    log_obj = FreeIPAHealthCheckLog(context_wrap(FREEIPA_HEALTHCHECK_LOG_FAILURES))
    results = log_obj.get_results('ipahealthcheck.system.filesystemspace', 'FileSystemSpaceCheck')
    assert len(results) == 1
    for result in results:
        assert result['result'] in ['ERROR', 'CRITICAL']
        assert result['check'] == 'FileSystemSpaceCheck'
        assert result['source'] == 'ipahealthcheck.system.filesystemspace'


def test_freeipa_healthcheck_log__documentation():
    env = {
        'healthcheck': FreeIPAHealthCheckLog(context_wrap(FREEIPA_HEALTHCHECK_LOG_DOCS_EXAMPLE)),
    }
    failed, total = doctest.testmod(freeipa_healthcheck_log, globs=env)
    assert failed == 0
