import json
import pytest

from mock.mock import Mock

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs
from insights.specs.datasources.semanage import LocalSpecs, users_count_map_selinux_user

SEMANGE_LOGIN_LIST_OUTPUT1 = """

Login Name           SELinux User         MLS/MCS Range        Service

%groupb               staff_u             s0-s0:c0.c1023       *
__default__          unconfined_u         s0-s0:c0.c1023       *
testa                staff_u              s0                   *
root                 unconfined_u         s0-s0:c0.c1023       *
"""

SEMANGE_LOGIN_LIST_OUTPUT2 = """

Login Name           SELinux User         MLS/MCS Range        Service

__default__          unconfined_u         s0-s0:c0.c1023       *
systemu              systemu              s0-s0:c0.c1023       *
root                 unconfined_u         s0-s0:c0.c1023       *
"""

RELATIVE_PATH = 'insights_commands/linux_users_count_map_selinux_user'


def setup_function(func):
    if Specs.selinux_users in filters._CACHE:
        del filters._CACHE[Specs.selinux_users]
    if Specs.selinux_users in filters.FILTERS:
        del filters.FILTERS[Specs.selinux_users]

    if func is test_linux_users_count_map_staff_u:
        filters.add_filter(Specs.selinux_users, ["staff_u"])
    if func is test_linux_users_count_map_more_selinux_users:
        filters.add_filter(Specs.selinux_users, ["staff_u", "unconfined_u"])
    if func is test_linux_users_count_map_staff_u_except:
        filters.add_filter(Specs.selinux_users, [])


def test_linux_users_count_map_staff_u():
    selinux_list = Mock()
    selinux_list.content = SEMANGE_LOGIN_LIST_OUTPUT1.splitlines()
    broker = {
        LocalSpecs.selinux_user_mapping: selinux_list
    }
    result = users_count_map_selinux_user(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    data = {'staff_u': 2}
    expected = DatasourceProvider(json.dumps(data), relative_path=RELATIVE_PATH)
    assert sorted(result.content) == sorted(expected.content)
    assert result.relative_path == expected.relative_path


def test_linux_users_count_map_more_selinux_users():
    selinux_list = Mock()
    selinux_list.content = SEMANGE_LOGIN_LIST_OUTPUT1.splitlines()
    broker = {
        LocalSpecs.selinux_user_mapping: selinux_list
    }
    result = users_count_map_selinux_user(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    data = {'staff_u': 2, "unconfined_u": 2}
    expected = DatasourceProvider(json.dumps(data), relative_path=RELATIVE_PATH)
    assert sorted(result.content) == sorted(expected.content)
    assert result.relative_path == expected.relative_path


def test_linux_users_count_map_staff_u_except():
    selinux_list = Mock()
    selinux_list.content = SEMANGE_LOGIN_LIST_OUTPUT2.splitlines()
    broker = {
        LocalSpecs.selinux_user_mapping: selinux_list
    }
    with pytest.raises(SkipComponent):
        users_count_map_selinux_user(broker)
