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

from insights import rule, make_fail
from insights.parsers.hostname import Hostname

ERROR_KEY = "INSIGHTS_HEARTBEAT"
HEARTBEAT_UUID = "9cd6f607-6b28-44ef-8481-62b0e7773614"
HOST = "insights-heartbeat-" + HEARTBEAT_UUID


@rule(Hostname)
def is_insights_heartbeat(hostname):
    hostname = hostname.hostname
    if hostname == HOST:
        return make_fail(ERROR_KEY)
