from insights.parsers.nova_log import NovaApiLog, NovaComputeLog
from insights.tests import context_wrap

from datetime import datetime

api_log = """
2016-08-12 13:15:46.343 32386 WARNING nova.api.ec2.cloud [-] Deprecated: The in tree EC2 API is deprecated as of Kilo release and may be removed in a future release. The stackforge ec2-api project http://git.openstack.org/cgit/stackforge/ec2-api/ is the target replacement for this functionality.
2016-08-12 14:27:16.498 32499 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
2016-08-12 14:27:16.500 32499 WARNING keystonemiddleware.auth_token [-] Identity response: {"error": {"message": "Could not find token: 786c3cee52d14baeae98262c6a2f3a4e", "code": 404, "title": "Not Found"}}
2016-08-12 14:27:16.502 32499 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
"""""


def test_nova_api_log():
    log = NovaApiLog(context_wrap(api_log))
    assert len(log.get(["WARNING", "Authorization failed"])) == 2
    assert len(log.get("786c3cee52d14baeae98262c6a2f3a4e")) == 1
    assert len(log.get("Authorization failed")) == 2
    assert len(list(log.get_after(datetime(2016, 8, 12, 14, 20, 0)))) == 3


def test_nova_compute_log():
    # use the same log file to do test. That is ok.
    log = NovaComputeLog(context_wrap(api_log))
    assert len(log.get(["WARNING", "Authorization failed"])) == 2
    assert len(log.get("786c3cee52d14baeae98262c6a2f3a4e")) == 1
    assert len(log.get("Authorization failed")) == 2
    assert len(list(log.get_after(datetime(2016, 8, 12, 14, 20, 0)))) == 3
