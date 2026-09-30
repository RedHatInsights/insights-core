import doctest
import json
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import sysroles_fingerprint
from insights.parsers.sysroles_fingerprint import SysrolesFingerprint
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


SYSROLES_FINGERPRINT_INVALID_JSON = """
{"date": "2026-08-03T10:15:00+02:00", "role_name": "redhat.rhel_system_roles.network", "status": "success"}
{"date": "2026-08-03T10:18:22+02:00", "role_name": "redhat.rhel_system_roles.timesync", "status": "success"
""".strip()


def test_sysroles_fingerprint_multiple_records():
    """Test parsing multiple JSONL records."""
    ret = SysrolesFingerprint(context_wrap(SYSROLES_JSONL))
    assert len(ret) == 2
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.network'
    assert ret[0]['status'] == 'success'
    assert ret[0]['play_hosts_number'] == 3
    assert ret[0]['ansible_check_mode'] is False
    assert ret[1]['role_name'] == 'redhat.rhel_system_roles.timesync'
    assert ret[1]['managed_node_distro'] == 'RedHat-9.4'


def test_sysroles_fingerprint_single_record():
    """Test parsing a single record."""
    ret = SysrolesFingerprint(context_wrap(SYSROLES_JSONL_SINGLE))
    assert len(ret) == 1
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.selinux'
    assert ret[0]['status'] == 'begin'
    assert ret[0]['ansible_check_mode'] is True
    assert ret[0]['managed_node_distro'] == 'RedHat-8.10'


def test_sysroles_fingerprint_role_path_indicates_ah():
    """Test that role_path can indicate Automation Hub collection."""
    ret = SysrolesFingerprint(context_wrap(SYSROLES_JSONL_CHECK_MODE))
    assert 'collections' in ret[0]['role_path']
    assert ret[0]['play_hosts_number'] == 10


def test_sysroles_fingerprint_empty():
    """Test that empty content raises SkipComponent."""
    with pytest.raises(SkipComponent) as exc:
        SysrolesFingerprint(context_wrap(''))
    assert "Empty output" in str(exc.value)


def test_sysroles_fingerprint_blank_lines_ignored():
    """Test that blank lines and whitespace-only lines are properly ignored."""
    content = '   \n\t\n' + SYSROLES_JSONL_SINGLE + '\n  \n\t\t\n'
    ret = SysrolesFingerprint(context_wrap(content))
    assert len(ret) == 1
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.selinux'


def test_sysroles_fingerprint_whitespace_only():
    """Test that whitespace-only content raises SkipComponent."""
    with pytest.raises(SkipComponent) as exc:
        SysrolesFingerprint(context_wrap('\n\n\n'))
    assert "Empty output" in str(exc.value)


def test_sysroles_fingerprint_invalid_json():
    """Test that invalid JSON raises ParseException."""
    with pytest.raises(ParseException) as exc:
        SysrolesFingerprint(context_wrap(SYSROLES_FINGERPRINT_INVALID_JSON))
    assert "Invalid JSON line" in str(exc.value)


def test_sysroles_fingerprint_non_dict_json():
    """Test that valid JSON non-dict types raise ParseException."""
    # Test array
    with pytest.raises(ParseException) as exc:
        SysrolesFingerprint(context_wrap('["array", "of", "strings"]'))
    assert "Invalid JSON line" in str(exc.value)

    # Test string
    with pytest.raises(ParseException) as exc:
        SysrolesFingerprint(context_wrap('"just a string"'))
    assert "Invalid JSON line" in str(exc.value)

    # Test number
    with pytest.raises(ParseException) as exc:
        SysrolesFingerprint(context_wrap('123'))
    assert "Invalid JSON line" in str(exc.value)

    # Test boolean
    with pytest.raises(ParseException) as exc:
        SysrolesFingerprint(context_wrap('true'))
    assert "Invalid JSON line" in str(exc.value)


def test_sysroles_fingerprint_lines_with_only_whitespace():
    """Test that empty lines between records are properly skipped."""
    # Create content with actual blank lines between valid JSON
    lines = SYSROLES_JSONL.split('\n')
    data_with_blank_lines = lines[0] + '\n\n' + lines[1]  # Insert blank line between two records
    ret = SysrolesFingerprint(context_wrap(data_with_blank_lines))
    assert len(ret) == 2
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.network'
    assert ret[1]['role_name'] == 'redhat.rhel_system_roles.timesync'


def test_sysroles_fingerprint_with_empty_json_objects():
    """Test that empty JSON objects are skipped."""
    data_with_empties = '\n'.join([
        '{}',
        SYSROLES_JSONL_SINGLE,
        '{}',
    ])
    ret = SysrolesFingerprint(context_wrap(data_with_empties))
    assert len(ret) == 1
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.selinux'


def test_sysroles_fingerprint_only_empty_objects():
    """Test that a file with only empty JSON objects raises SkipComponent."""
    only_empties = '\n'.join(['{}', '{}', '{}'])
    with pytest.raises(SkipComponent) as exc:
        SysrolesFingerprint(context_wrap(only_empties))
    assert "No parsable data found" in str(exc.value)


def test_sysroles_fingerprint_null_raises_exception():
    """Test that null values raise ParseException."""
    with pytest.raises(ParseException) as exc:
        SysrolesFingerprint(context_wrap('null'))
    assert "Invalid JSON line" in str(exc.value)


def test_sysroles_fingerprint_minimal_fields():
    """Test that records with minimal fields work."""
    minimal_data = '{"role_name": "redhat.rhel_system_roles.network", "status": "success"}'
    ret = SysrolesFingerprint(context_wrap(minimal_data))
    assert len(ret) == 1
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.network'
    assert ret[0]['status'] == 'success'


def test_sysroles_fingerprint_extra_fields_preserved():
    """Test that extra/unknown fields are preserved (forward compatibility)."""
    extra_fields = '{"role_name": "test", "status": "success", "unknown_field": "value", "another_field": 123}'
    ret = SysrolesFingerprint(context_wrap(extra_fields))
    assert len(ret) == 1
    assert ret[0]['role_name'] == 'test'
    assert ret[0]['status'] == 'success'
    # Extra fields are preserved for forward compatibility
    assert ret[0]['unknown_field'] == 'value'
    assert ret[0]['another_field'] == 123


def test_sysroles_fingerprint_complex_nested_data():
    """Test that records with nested structures are preserved."""
    complex_data = '\n'.join([
        json.dumps({
            "date": "2026-08-03T10:15:00+02:00",
            "role_name": "redhat.rhel_system_roles.network",
            "status": "success",
            "config": {"interfaces": ["eth0", "eth1"]},
        }),
        json.dumps({
            "date": "2026-08-03T10:18:22+02:00",
            "role_name": "redhat.rhel_system_roles.selinux",
            "status": "success",
            "ansible_version": "2.16.3",
            "config": {"mode": "enforcing", "booleans": {"httpd_can_network_connect": True}},
        }),
    ])
    ret = SysrolesFingerprint(context_wrap(complex_data))
    assert len(ret) == 2
    # All fields are preserved
    assert ret[0]['role_name'] == 'redhat.rhel_system_roles.network'
    assert ret[0]['status'] == 'success'
    assert ret[0]['date'] == '2026-08-03T10:15:00+02:00'
    assert ret[0]['config']['interfaces'] == ['eth0', 'eth1']
    # Second record
    assert ret[1]['ansible_version'] == '2.16.3'
    assert ret[1]['config']['booleans']['httpd_can_network_connect'] is True


def test_doc_examples():
    """Test documentation examples."""
    env = {
        'sysroles_fingerprint': SysrolesFingerprint(context_wrap(SYSROLES_JSONL)),
    }
    failed, total = doctest.testmod(sysroles_fingerprint, globs=env)
    assert failed == 0
