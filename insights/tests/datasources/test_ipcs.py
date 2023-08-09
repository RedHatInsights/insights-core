import pytest

from mock.mock import Mock

from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.specs.datasources import ipcs


IPCS_OUTPUT1 = """

------ Semaphore Arrays --------
key        semid      owner      perms      nsems
0x00000000 65570      apache     600        1
0x00000000 98353      apache     600        1
0x00000000 28         fxadmin    0          1
0x0052e2c1 89998      oracle     600        26
0x00000000 98354      apache     600        1
0x00000000 98355      apache     600        1
0x00000000 98356      apache     600        1
0x00000000 98357      apache     600        1
""".strip()

IPCS_OUTPUT2 = """

------ Semaphore Arrays --------
key        semid      owner      perms      nsems
""".strip()


def test_semid():
    ipcs_command = Mock()
    ipcs_command.content = IPCS_OUTPUT1.splitlines()
    broker = {Specs.ipcs_s: ipcs_command}
    result = ipcs.semid(broker)
    assert result is not None
    assert isinstance(result, list)
    assert '65570' in result
    assert '98357' in result
    assert '89998' in result
    assert '28' not in result
    assert len(result) == 7


def test_exception():
    ipcs_command = Mock()
    ipcs_command.content = IPCS_OUTPUT2.splitlines()
    broker = {Specs.ipcs_s: ipcs_command}
    with pytest.raises(SkipComponent):
        ipcs.semid(broker)
