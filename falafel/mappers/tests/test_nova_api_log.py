from falafel.mappers.nova_api_log import NovaApiLog
from falafel.tests import context_wrap

api_log = """
2016-08-12 13:15:46.343 32386 WARNING nova.api.ec2.cloud [-] Deprecated: The in tree EC2 API is deprecated as of Kilo \
release and may be removed in a future release. The stackforge ec2-api project http://git.openstack.org/cgit/stackforge\
/ec2-api/ is the target replacement for this functionality.
2016-08-12 14:27:16.498 32499 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
2016-08-12 14:27:16.500 32499 WARNING keystonemiddleware.auth_token [-] Identity response: {"error": {"message": \
"Could not find token: 786c3cee52d14baeae98262c6a2f3a4e", "code": 404, "title": "Not Found"}}
2016-08-12 14:27:16.502 32499 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
"""""


def test_nova_api_log():
    log = NovaApiLog.parse_context(context_wrap(api_log))
    assert len(log.get(["WARNING", "Authorization failed"])) == 2
    assert len(log.get("786c3cee52d14baeae98262c6a2f3a4e")) == 1
    assert len(log.get("Authorization failed")) == 2
