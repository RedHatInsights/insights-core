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

from insights.parsers import docker_host_machine_id
from insights.tests import context_wrap

DOCKER_HOST_MACHINE_ID = """
e6637bbb-ae92-46f8-a249-92d184c5fc24
"""


def test_docker_host_machine_id():
    machine_id = docker_host_machine_id.docker_host_machineid_parser(context_wrap(DOCKER_HOST_MACHINE_ID))
    assert machine_id.get("host_system_id") == "e6637bbb-ae92-46f8-a249-92d184c5fc24"
