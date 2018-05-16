from __future__ import print_function
from insights.parsers import openshift_logs
from insights.tests import context_wrap

from datetime import datetime

LOG_LINES = """
2018-05-15T03:19:42.020507000Z I0515 03:19:42.006017       1 template.go:246] Starting template router (v3.6.173.0.112)
2018-05-15T03:19:42.974500000Z I0515 03:19:42.970212       1 router.go:554] Router reloaded:
2018-05-15T03:19:42.974827000Z  - Checking http://localhost:80 ...
2018-05-15T03:19:42.975175000Z  - Health check ok : 0 retry attempt(s).
2018-05-15T03:19:42.975431000Z I0515 03:19:42.970321       1 router.go:240] Router is including routes in all namespaces
2018-05-15T03:20:04.678579000Z I0515 03:20:04.677674       1 router.go:554] Router reloaded:
2018-05-15T03:20:04.678932000Z  - Checking http://localhost:80 ...
2018-05-15T03:20:04.679176000Z  - Health check ok : 0 retry attempt(s).
2018-05-15T03:26:30.172078000Z E0515 03:26:30.171576       1 ratelimiter.go:52] error reloading router: exit status 1
2018-05-15T03:26:30.172338000Z  - Checking http://localhost:80 ...
2018-05-15T03:26:30.172585000Z  - Exceeded max wait time (30) in health check - 58 retry attempt(s).
2018-05-15T03:27:32.246522000Z E0515 03:27:32.245964       1 ratelimiter.go:52] error reloading router: exit status 1
2018-05-15T03:27:32.247014000Z  - Checking http://localhost:80 ...
2018-05-15T03:27:32.247432000Z  - Exceeded max wait time (30) in health check - 57 retry attempt(s).
"""


def test_openshift_logs_dc_router():
    logs = openshift_logs.OpenShiftDcRouterLogs(context_wrap(LOG_LINES))
    assert len(logs) == 14
    reloaded = logs.get("Router reloaded")
    assert reloaded[0] == {
        'raw_message': '2018-05-15T03:19:42.974500000Z I0515 03:19:42.970212       1 router.go:554] Router reloaded:',
        'timestamp': '2018-05-15T03:19:42.974500000Z',
        'message': 'I0515 03:19:42.970212       1 router.go:554] Router reloaded:'
    }
    checking = logs.get("Checking http://localhost:80")
    assert checking[2] == {
        'raw_message': '2018-05-15T03:26:30.172338000Z  - Checking http://localhost:80 ...',
        'timestamp': '2018-05-15T03:26:30.172338000Z',
        'message': ' - Checking http://localhost:80 ...'
    }
    assert len(list(logs.get_after(datetime(2018, 5, 15, 3, 21, 0)))) == 6
