import doctest
from insights.parsers import freeipa_healthcheck_log
from insights.parsers.freeipa_healthcheck_log import FreeIPAHealthCheckLog
from insights.tests import context_wrap

LONG_FREEIPA_HEALTHCHECK_LOG_OK = """
[{"source": "ipahealthcheck.meta.services", "check": "certmonger",
"severity": 0, "uuid": "693c526c-2261-44fe-98e0-94c6b76bf79b",
"when": "20190711141703Z", "duration": "0.012848", "kw": {"status": true}}]
""".strip()

LONG_FREEIPA_HEALTHCHECK_LOG_FAILURES = """
[{"source": "ipahealthcheck.system.filesystemspace", "check": "FileSystemSpaceCheck",
"severity": 2, "uuid": "ceadd564-f42f-4640-a3ae-b67f1aa29dc4", "when": "20190711141807Z",
"duration": null, "kw": {"msg": "/var/log/: free space under threshold: 400 MiB < 1024 MiB",
"store": "/var/log/", "free_space": 400, "threshold": 1024}}]
""".strip()

FREEIPA_HEALTHCHECK_LOG_DOCS_EXAMPLE = '''
    [
      {
        "source": "ipahealthcheck.dogtag.ca",
        "check": "DogtagCertsConfigCheck",
        "severity": 0,
        "uuid": "57f7d2c9-f71f-4c2f-b831-9e30250b18b2",
        "when": "20190726213428Z",
        "duration": "0.150333",
        "kw": {
          "key": "subsystemCert cert-pki-ca",
          "configfile": "/var/lib/pki/pki-tomcat/conf/ca/CS.cfg"
        }
      },
      {
        "source": "ipahealthcheck.ipa.certs",
        "check": "IPACertmongerExpirationCheck",
        "severity": 0,
        "uuid": "afd047c2-d78b-4c5c-b3a4-f68578ee1595",
        "when": "20190726213429Z",
        "duration": "0.007105",
        "kw": {
          "key": "20190620165230"
        }
      },
      {
        "source": "ipahealthcheck.ds.replication",
        "check": "ReplicationConflictCheck",
        "severity": 0,
        "uuid": "99c0a513-447c-46f1-95ea-058fc0db6075",
        "when": "20190726213429Z",
        "duration": "0.001409",
        "kw": {}
      },
      {
        "source": "ipahealthcheck.ipa.files",
        "check": "IPAFileNSSDBCheck",
        "severity": 0,
        "uuid": "7e8a7739-c4d6-4b97-b602-9f9e981f793c",
        "when": "20190726213432Z",
        "duration": "0.000765",
        "kw": {
          "key": "_etc_pki_pki-tomcat_alias_cert9.db_owner",
          "type": "owner",
          "path": "/etc/pki/pki-tomcat/alias/cert9.db"
        }
      },
      {
        "source": "ipahealthcheck.ipa.topology",
        "check": "IPATopologyDomainCheck",
        "severity": 0,
        "uuid": "c5ee8ee1-98d1-4696-bbf1-8243677b8918",
        "when": "20190726213432Z",
        "duration": "0.019070",
        "kw": {
          "suffix": "ca"
        }
      },
      {
        "source": "ipahealthcheck.system.filesystemspace",
        "check": "FileSystemSpaceCheck",
        "severity": 2,
        "uuid": "4d1c71c5-cc37-4ebf-b53c-34f4e4534437",
        "when": "20190726213432Z",
        "duration": null,
        "kw": {
          "msg": "/var/lib/dirsrv/: free space percentage under threshold: 1% < 20%",
          "store": "/var/lib/dirsrv/",
          "percent_free": 1,
          "threshold": 20
        }
      }
    ]
'''.strip()


FREEIPA_HEALTHCHECK_LOG_OK = "".join(LONG_FREEIPA_HEALTHCHECK_LOG_OK.splitlines())
FREEIPA_HEALTHCHECK_LOG_FAILURES = "".join(LONG_FREEIPA_HEALTHCHECK_LOG_FAILURES.splitlines())


def test_freeipa_healthcheck_log_ok():
    log_obj = FreeIPAHealthCheckLog(context_wrap(FREEIPA_HEALTHCHECK_LOG_OK))
    assert len(log_obj.errors) == 0


def test_freeipa_healthcheck_log_not_ok():
    log_obj = FreeIPAHealthCheckLog(context_wrap(FREEIPA_HEALTHCHECK_LOG_FAILURES))
    assert len(log_obj.errors) > 0
    for error in log_obj.errors:
        assert error['check'] == 'FileSystemSpaceCheck'
        assert error['source'] == 'ipahealthcheck.system.filesystemspace'


def test_freeipa_healthcheck_log__documentation():
    env = {
        'healthcheck': FreeIPAHealthCheckLog(context_wrap(FREEIPA_HEALTHCHECK_LOG_DOCS_EXAMPLE)),
    }
    failed, total = doctest.testmod(freeipa_healthcheck_log, globs=env)
    assert failed == 0
