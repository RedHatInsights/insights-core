import doctest
from datetime import datetime

from insights import add_filter
from insights.parsers import rhsm_log
from insights.parsers.rhsm_log import RhsmLog
from insights.specs import Specs
from insights.tests import context_wrap

LOG1 = """
2016-07-31 04:06:41,215 [DEBUG] rhsmcertd-worker:24440 @identity.py:131 - Loading consumer info from identity certificates.
2016-07-31 04:06:41,221 [DEBUG] rhsmcertd-worker:24440 @connection.py:475 - Loaded CA certificates from /etc/rhsm/ca/: redhat-uep.pem
2016-07-31 04:06:41,221 [DEBUG] rhsmcertd-worker:24440 @connection.py:523 - Making request: GET /subscription/consumers/a808d48e-36bf-4071-a00a-0efacc511b2b/certificates/serials
2016-07-31 04:07:21,245 [ERROR] rhsmcertd-worker:24440 @entcertlib.py:121 - [Errno -2] Name or service not known
""".strip()

LOG2 = """
2011-12-27 08:41:12,460 [DEBUG]  @connection.py:209 - Making request: GET /subscription/users/isavia_sysdep/owners
2011-12-27 08:41:13,104 [ERROR]  @managercli.py:65 - Error during registration: certificate verify failed
2011-12-27 08:41:13,104 [ERROR]  @managercli.py:66 - certificate verify failed
    Traceback (most recent call last):
    File "/usr/share/rhsm/subscription_manager/managercli.py", line 600, in _do_command
""".strip()

# For Coverage
LOG3 = """
[ERROR]
2011-12-27-08:41:13,104 [ERROR]  @managercli.py:66 - certificate verify failed
"""

add_filter(Specs.rhsm_log, [
    "[ERROR]",
    "[Errno"
])


def test_rhsm_log():
    rlog = RhsmLog(context_wrap(LOG1))
    ern_list = rlog.get('[Errno -2]')
    assert 1 == len(ern_list)
    assert ern_list[0]['raw_message'] == "2016-07-31 04:07:21,245 [ERROR] rhsmcertd-worker:24440 @entcertlib.py:121 - [Errno -2] Name or service not known"
    assert ern_list[0]['timestamp'] == datetime(2016, 7, 31, 4, 7, 21, 245000)
    assert ern_list[0]['message'] == "[ERROR] rhsmcertd-worker:24440 @entcertlib.py:121 - [Errno -2] Name or service not known"

    rlog = RhsmLog(context_wrap(LOG2))
    ern_list = rlog.get('[Errno -2]')
    assert 0 == len(ern_list)
    err_list = rlog.get('ERROR')
    assert 2 == len(err_list)

    rlog = RhsmLog(context_wrap(LOG3))
    err_list = rlog.get('ERROR')
    assert err_list[0].get('timestamp') is None
    assert err_list[1].get('timestamp') is None


def test_doc():
    failed_count, tests = doctest.testmod(
        rhsm_log, globs={'rhsm_log': RhsmLog(context_wrap(LOG1))}
    )
    assert failed_count == 0
