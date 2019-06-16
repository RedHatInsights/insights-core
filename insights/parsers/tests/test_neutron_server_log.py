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

from insights.parsers.neutron_server_log import NeutronServerLog
from insights.tests import context_wrap

NEUTRON_LOG = """
2016-09-13 05:56:45.155 30586 WARNING keystonemiddleware.auth_token [-] Identity response: {"error": {"message": "Could not find token: b45405915eb44e608885f894028d37b9", "code": 404, "title": "Not Found"}}
2016-09-13 05:56:45.156 30586 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
2016-09-13 06:06:45.884 30588 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
2016-09-13 06:06:45.886 30588 WARNING keystonemiddleware.auth_token [-] Identity response: {"error": {"message": "Could not find token: fd482ef0ba1144bf944a0a6c2badcdf8", "code": 404, "title": "Not Found"}}
2016-09-13 06:06:45.887 30588 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
2016-09-13 06:06:46.131 30586 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
2016-09-13 06:06:46.131 30586 WARNING keystonemiddleware.auth_token [-] Identity response: {"error": {"message": "Could not find token: bc029dbe33f84fbcb67ef7d592458e60", "code": 404, "title": "Not Found"}}
2016-09-13 06:06:46.132 30586 WARNING keystonemiddleware.auth_token [-] Authorization failed for token
""".strip()


def test_server_log():
    neutron_server = NeutronServerLog(context_wrap(NEUTRON_LOG))
    assert len(neutron_server.get(["WARNING", "Authorization failed for token"])) == 5
    assert len(neutron_server.get(["Identity response:"])) == 3
    assert len(neutron_server.get("Identity response:")) == 3
