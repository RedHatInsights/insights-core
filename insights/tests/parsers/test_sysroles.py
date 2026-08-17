import doctest
import json
import pytest

from insights.parsers import sysroles
from insights.parsers.sysroles import SysrolesFingerprint
from insights.core.exceptions import SkipComponent
from insights.tests import context_wrap


SYSROLES_JSONL = '\n'.join([
    json.dumps({
        "date": "2026-08-03T10:15:00+02:00",
        "role_name": "redhat.rhel_system_roles.network",
        "role_path": "/usr/share/ansible/roles/linux-system-roles.network",
        "status": "success",
        "ansible_version": "2.16.3",
        "managed_node_distro": "RedHat-9.4",
        "play_hosts_number": 3,
        "ansible_check_mode": False,
    }),
    json.dumps({
        "date": "2026-08-03T10:18:22+02:00",
        "role_name": "redhat.rhel_system_roles.timesync",
        "role_path": "/usr/share/ansible/roles/linux-system-roles.timesync",
        "status": "success",
        "ansible_version": "2.16.3",
        "managed_node_distro": "RedHat-9.4",
        "play_hosts_number": 3,
        "ansible_check_mode": False,
    }),
])

SYSROLES_JSONL_SINGLE = json.dumps({
    "date": "2026-07-01T08:00:00+00:00",
    "role_name": "redhat.rhel_system_roles.selinux",
    "role_path": "/usr/share/ansible/roles/linux-system-roles.selinux",
    "status": "begin",
    "ansible_version": "2.17.0",
    "managed_node_distro": "RedHat-8.10",
    "play_hosts_number": 1,
    "ansible_check_mode": True,
})

SYSROLES_JSONL_CHECK_MODE = json.dumps({
    "date": "2026-08-10T12:00:00+00:00",
    "role_name": "redhat.rhel_system_roles.firewall",
    "role_path": "/home/user/.ansible/collections/ansible_collections/redhat/rhel_system_roles/roles/firewall",
    "status": "success",
    "ansible_version": "2.16.3",
    "managed_node_distro": "RedHat-9.4",
    "play_hosts_number": 10,
    "ansible_check_mode": True,
})


def test_sysroles_fingerprint_multiple_records():
    ret = SysrolesFingerprint(context_wrap(SYSROLES_JSONL))
    assert len(ret) == 2
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.network'
    assert ret[0]['status'] == 'success'
    assert ret[0]['play_hosts_number'] == 3
    assert ret[0]['ansible_check_mode'] is False
    assert ret[1]['role_name'] == 'redhat.rhel_system_roles.timesync'


def test_sysroles_fingerprint_single_record():
    ret = SysrolesFingerprint(context_wrap(SYSROLES_JSONL_SINGLE))
    assert len(ret) == 1
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.selinux'
    assert ret[0]['status'] == 'begin'
    assert ret[0]['ansible_check_mode'] is True
    assert ret[0]['managed_node_distro'] == 'RedHat-8.10'


def test_sysroles_fingerprint_role_path_indicates_ah():
    ret = SysrolesFingerprint(context_wrap(SYSROLES_JSONL_CHECK_MODE))
    assert 'collections' in ret[0]['role_path']


def test_sysroles_fingerprint_empty_raises():
    with pytest.raises(SkipComponent):
        SysrolesFingerprint(context_wrap(''))


def test_sysroles_fingerprint_blank_lines_ignored():
    content = '\n\n' + SYSROLES_JSONL_SINGLE + '\n\n'
    ret = SysrolesFingerprint(context_wrap(content))
    assert len(ret) == 1


def test_doc_examples():
    env = {
        'sysroles_fingerprint': SysrolesFingerprint(context_wrap(SYSROLES_JSONL)),
    }
    failed, total = doctest.testmod(sysroles, globs=env)
    assert failed == 0
