import pytest
import doctest
from insights.parsers import SkipException, openstack_server_list_all
from insights.tests import context_wrap
from insights.parsers.openstack_server_list_all import OpenstackServerListAll


VALID_TABLE = """
 +--------------------------------------+--------------+--------+------------------------+----------------+------------+
 | ID                                   | Name         | Status | Networks               | Image          | Flavor     |
 +--------------------------------------+--------------+--------+------------------------+----------------+------------+
 | 410b05bb-59b7-4b4c-88e9-975c811d68da | compute-0    | ACTIVE | ctlplane=192.168.24.20 | overcloud-full | compute    |
 | f891e98b-4df6-4c90-9bf1-39cf8ac900b0 | compute-1    | ACTIVE | ctlplane=192.168.24.9  | overcloud-full | compute    |
 | 3d62cd7e-41d2-43dd-a5bf-5935bc319fae | controller-0 | ACTIVE | ctlplane=192.168.24.10 | overcloud-full | controller |
 +--------------------------------------+--------------+--------+------------------------+----------------+------------+
 """


def test_empty_openstack_server_list():
    with pytest.raises(SkipException) as e_info:
        OpenstackServerListAll(context_wrap(""))
    assert "Empty content." in str(e_info.value)


def test_openstack_server_list_options():
    parser_result = OpenstackServerListAll(context_wrap(VALID_TABLE))
    parser_data = parser_result.data
    assert len(parser_data) == 3
    assert parser_data[0] == {
        'ID': '410b05bb-59b7-4b4c-88e9-975c811d68da',
        'Name': 'compute-0',
        'Status': 'ACTIVE',
        'Networks': 'ctlplane=192.168.24.20',
        'Image': 'overcloud-full',
        'Flavor': 'compute'
    }
    assert parser_data[1]["Name"] == 'compute-1'
    assert parser_data[1]["Image"] == 'overcloud-full'
    assert parser_data[1]["Flavor"] == 'compute'
    assert parser_data[0]["Networks"] == 'ctlplane=192.168.24.20'
    assert parser_result.get_list('Name') == ['compute-0', 'compute-1', 'controller-0']
    assert parser_result.get_startwith('Name', 'controller') == ['controller-0']
    assert parser_result.get_startwith('Name', 'compute') == ['compute-0', 'compute-1']


def test_doc():
    INFO = VALID_TABLE
    env = {
            "parser_result_server_list": OpenstackServerListAll(context_wrap(INFO)),
    }
    failed, total = doctest.testmod(openstack_server_list_all, globs=env)
    assert failed == 0
