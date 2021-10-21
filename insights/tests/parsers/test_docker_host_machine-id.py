from insights.parsers import docker_host_machine_id
from insights.tests import context_wrap

DOCKER_HOST_MACHINE_ID = """
e6637bbb-ae92-46f8-a249-92d184c5fc24
"""


def test_docker_host_machine_id():
    machine_id = docker_host_machine_id.docker_host_machineid_parser(context_wrap(DOCKER_HOST_MACHINE_ID))
    assert machine_id.get("host_system_id") == "e6637bbb-ae92-46f8-a249-92d184c5fc24"
