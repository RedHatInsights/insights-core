from insights.parsers.glance_log import GlanceApiLog
from insights.tests import context_wrap

from datetime import datetime

API_LOG = """
2016-11-09 14:36:35.618 26656 WARNING oslo_config.cfg [-] Option "rpc_backend" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
2016-11-09 14:36:38.717 26656 INFO glance.common.wsgi [-] Starting 4 workers
2016-11-09 14:36:38.737 27285 INFO eventlet.wsgi.server [-] (27285) wsgi starting up on http://172.18.0.13:9292
2016-11-09 14:36:38.737 26656 INFO glance.common.wsgi [-] Started child 27285
"""


def test_glance_api_log():
    log = GlanceApiLog(context_wrap(API_LOG))
    assert len(log.get('INFO')) == 3
    assert len(list(log.get_after(datetime(2016, 11, 9, 14, 36, 38)))) == 3
