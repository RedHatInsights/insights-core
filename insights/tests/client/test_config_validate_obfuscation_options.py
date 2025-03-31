import pytest

try:
    from unittest.mock import patch
except Exception:
    from mock import patch

from insights.client.config import InsightsConfig


@pytest.mark.parametrize(
    ("obfuscate", "obfuscate_hostname", "obfuscation_list", "expected_opt"),
    [
        (None, None, None, []),
        (False, False, None, []),
        (None, None, '', []),
        (True, True, None, ['ipv4', 'hostname']),
        (True, False, None, ['ipv4']),
        (None, None, 'ipv6, hostname, ipv4', ['hostname', 'ipv4', 'ipv6']),
        (None, None, 'ipv4,ipv6,hostname,mac', ['hostname', 'ipv4', 'ipv6', 'mac']),
    ],
)
def test_validate_obfuscation_options_good(
    obfuscate, obfuscate_hostname, obfuscation_list, expected_opt
):
    c = InsightsConfig(
        obfuscate=obfuscate,
        obfuscate_hostname=obfuscate_hostname,
        obfuscation_list=obfuscation_list,
    )
    assert c.obfuscation_list == expected_opt
    assert c.obfuscate is None
    assert c.obfuscate_hostname is None


@patch('insights.client.config.sys.stdout.write')
@patch('insights.client.config.get_rhel_version', return_value=10)
@patch('insights.client.config.get_version_info', return_value={'core_version': '3.6.0-1'})
def test_validate_obfuscation_options_conflict_old_warning(egg, rhel, sys_write):
    with pytest.raises(ValueError) as ve:
        InsightsConfig(obfuscate=False, obfuscate_hostname=True, _print_errors=True)
    assert 'Option `obfuscate_hostname` requires `obfuscate`' in str(ve.value)
    sys_write.assert_called_once_with(
        'WARNING: `obfuscate` and `obfuscate_hostname` are deprecated, please use `obfuscation_list` instead.\n'
    )


@patch('insights.client.config.sys.stdout.write')
@patch('insights.client.config.get_rhel_version', return_value=10)
@patch('insights.client.config.get_version_info', return_value={'core_version': '3.5.10-1'})
def test_validate_obfuscation_options_conflict_old_no_warning(egg, rhel, sys_write):
    InsightsConfig(obfuscate=True, obfuscate_hostname=True, _print_errors=True)
    sys_write.assert_not_called()


@patch('insights.client.config.sys.stdout.write')
@patch('insights.client.config.get_rhel_version', return_value=7)
@patch('insights.client.config.get_version_info', return_value={'core_version': '3.6.10-1'})
def test_validate_obfuscation_options_conflict_old_rhel7(egg, rhel, sys_write):
    with pytest.raises(ValueError) as ve:
        InsightsConfig(obfuscate=False, obfuscate_hostname=True, _print_errors=True)
    assert 'Option `obfuscate_hostname` requires `obfuscate`' in str(ve.value)
    sys_write.assert_not_called()


@pytest.mark.parametrize(
    ("obfuscate", "obfuscate_hostname", "obfuscation_list"),
    [
        (True, True, ''),
        (True, False, ''),
        (False, False, ''),
        (True, True, 'ipv6, hostname, ipv4'),
        (False, False, 'ipv4,ipv6,hostname,mac'),
    ],
)
def test_validate_obfuscation_options_conflict_new(obfuscate, obfuscate_hostname, obfuscation_list):
    with pytest.raises(ValueError) as ve:
        InsightsConfig(
            obfuscate=obfuscate,
            obfuscate_hostname=obfuscate_hostname,
            obfuscation_list=obfuscation_list,
        )
    assert 'Conflicting options: `obfuscation_list` and `obfuscate`' in str(ve.value)


@patch('insights.client.config.sys.stdout.write')
def test_validate_obfuscation_options_new_invalid(sys_write):
    InsightsConfig(obfuscation_list=['mac', 'abc', 'ipv4'], _print_errors=True)
    sys_write.assert_called_once_with(
        'WARNING: ignoring invalid obfuscate options: `abc`, using: "obfuscation_list=ipv4,mac"\n'
    )
