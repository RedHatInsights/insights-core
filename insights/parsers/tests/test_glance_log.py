#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
