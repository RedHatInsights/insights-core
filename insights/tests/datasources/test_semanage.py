import pytest
from mock.mock import Mock

from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.semanage import LocalSpecs, users_count_map_staff_u_selinux_user

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

RELATIVE_PATH = 'insights_commands/linux_users_count_map_staff_u_selinux_user'


def test_linux_users_count_map_staff_u():
    selinux_list = Mock()
    selinux_list.content = SEMANGE_LOGIN_LIST_OUTPUT1.splitlines()
    broker = {
        LocalSpecs.selinux_user_mapping: selinux_list
    }
    result = users_count_map_staff_u_selinux_user(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content='2', relative_path=RELATIVE_PATH)
    assert sorted(result.content) == sorted(expected.content)
    assert result.relative_path == expected.relative_path


def test_linux_users_count_map_staff_u_except():
    selinux_list = Mock()
    selinux_list.content = SEMANGE_LOGIN_LIST_OUTPUT2.splitlines()
    broker = {
        LocalSpecs.selinux_user_mapping: selinux_list
    }
    with pytest.raises(SkipComponent):
        users_count_map_staff_u_selinux_user(broker)
