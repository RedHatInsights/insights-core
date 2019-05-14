import doctest

from insights.parsers import swift_log
from insights.tests import context_wrap

SWIFT_LOG_CONTENT = """
Mar  1 13:53:47 u1lab5 proxy-server: Adding required filter listing_formats to pipeline at position 4
Mar  1 13:53:47 u1lab5 proxy-server: Adding required filter gatekeeper to pipeline at position 1
Mar  1 13:53:47 u1lab5 proxy-server: Pipeline was modified. New pipeline is "catch_errors gatekeeper healthcheck proxy-logging cache listing_formats ratelimit bulk tempurl formpost authtoken keystone staticweb copy slo dlo versioned_writes proxy-logging proxy-server".
Mar  1 13:53:47 u1lab5 proxy-server: object_post_as_copy=true is deprecated; This option is now ignored
Mar  1 13:53:47 u1lab5 proxy-server: Starting Keystone auth_token middleware
Mar  1 13:53:47 u1lab5 proxy-server: Started child 25651
Mar  1 13:53:47 u1lab5 proxy-server: Adding required filter listing_formats to pipeline at position 4
Mar  1 13:53:47 u1lab5 proxy-server: Adding required filter gatekeeper to pipeline at position 1
Mar  1 13:53:47 u1lab5 proxy-server: Pipeline was modified. New pipeline is "catch_errors gatekeeper healthcheck proxy-logging cache listing_formats ratelimit bulk tempurl formpost authtoken keystone staticweb copy slo dlo versioned_writes proxy-logging proxy-server".
Mar  1 13:53:47 u1lab5 proxy-server: Adding required filter listing_formats to pipeline at position 4
Mar  1 13:53:47 u1lab5 proxy-server: Adding required filter gatekeeper to pipeline at position 1
Mar  1 13:53:47 u1lab5 proxy-server: Adding required filter listing_formats to pipeline at position 4
Mar  1 13:53:47 u1lab5 proxy-server: Pipeline was modified. New pipeline is "catch_errors gatekeeper healthcheck proxy-logging cache listing_formats ratelimit bulk tempurl formpost authtoken keystone staticweb copy slo dlo versioned_writes proxy-logging proxy-server".
Mar  1 14:49:13 u1lab5 container-server: 10.40.28.2 - - [01/Mar/2019:14:49:13 +0000] "DELETE /1/177/.expiring_objects/1551398391" 409 - "DELETE http://localhost/v1/.expiring_objects/1551398391" "txdd303f0a04264ca9b9921-005c794669" "proxy-server 25600" 0.0009 "-" 27659 -
Oct  2 09:10:43 u1lab5 object-expirer: STDERR: ERROR:root:Error talking to memcached: [Errno 32] Broken pipe (txn: tx015dd5a60bfa491d8eb09-005bb36e53)
""".strip()

SAMPLE_LOG = """
Sep 29 23:50:29 rh-server object-server: Starting object replication pass.
Sep 29 23:50:29 rh-server object-server: Nothing replicated for 0.01691198349 seconds.
Sep 29 23:50:29 rh-server object-server: Object replication complete. (0.00 minutes)
Sep 29 23:50:38 rh-server container-server: Beginning replication run
Sep 29 23:50:38 rh-server container-server: Replication run OVER
Sep 29 23:50:38 rh-server container-server: Attempted to replicate 0 dbs in 0.00064 seconds (0.00000/s)
""".strip()


def test_swift_log():
    log = swift_log.SwiftLog(context_wrap(SWIFT_LOG_CONTENT))
    assert "Starting Keystone auth_token middleware" in log
    obj_expirer_lines = log.get("object-expirer")
    assert len(obj_expirer_lines) == 1
    assert obj_expirer_lines[0].get("procname") == "object-expirer"
    assert obj_expirer_lines[0].get("timestamp") == "Oct 2 09:10:43"
    assert obj_expirer_lines[0].get("message") == "STDERR: ERROR:root:Error talking to memcached: [Errno 32] Broken pipe (txn: tx015dd5a60bfa491d8eb09-005bb36e53)"

    log_line = 'Sep 29 23:50:55 pbnec2-l-rh-ocld-2 object-server: Begin object audit "forever" mode (ALL)'
    log = swift_log.SwiftLog(context_wrap(log_line))
    assert "Begin object audit" in log
    assert log.get("Begin object audit")[0]['raw_message'] == log_line


def test_documentation():
    failed_count, tests = doctest.testmod(
        swift_log,
        globs={'swift_log': swift_log.SwiftLog(context_wrap(SAMPLE_LOG))}
    )
    assert failed_count == 0
