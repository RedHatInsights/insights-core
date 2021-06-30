from insights.parsers.ipcs import IpcsS
from insights.tests import context_wrap
from insights.specs.datasources import get_semid

IPCS_OUTPUT1 = """

------ Semaphore Arrays --------
key        semid      owner      perms      nsems
0x00000000 65570      apache     600        1
0x00000000 98353      apache     600        1
0x00000000 98354      apache     600        1
0x00000000 98355      apache     600        1
0x00000000 98356      apache     600        1
0x00000000 98357      apache     600        1
""".strip()

IPCS_OUTPUT2 = """

------ Semaphore Arrays --------
key        semid      owner      perms      nsems
""".strip()


def test_getsemid():
    ipcs_s_obj = IpcsS(context_wrap(IPCS_OUTPUT1))
    broker = {IpcsS: ipcs_s_obj}
    result = get_semid.get_semid(broker)
    assert result is not None
    assert isinstance(result, list)
    assert '65570' in result
    assert '98357' in result
    assert len(result) == 6
