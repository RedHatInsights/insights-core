import pytest

try:
    from unittest.mock import patch
except Exception:
    from mock import patch

from insights.client.config import InsightsConfig


@pytest.mark.parametrize(
    ("obfuscate", "obfuscate_hostname", "obfuscation_list", "expected_opt"),
    [
        (None, None, None, None),
        (False, False, None, []),
        ('False', 'False', None, []),
        ('0', '0', None, []),
        ('NO', 'No', None, []),
        (None, None, '', []),
        (True, True, None, ['ipv4', 'hostname']),
        ('True', 'True', None, ['ipv4', 'hostname']),
        ('YES', 'yes', None, ['ipv4', 'hostname']),
        (True, False, None, ['ipv4']),
        ('true', 'FALSE', None, ['ipv4']),
        ('1', '0', None, ['ipv4']),
        ('Yes', 'no', None, ['ipv4']),
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


@patch('insights.client.config.logger')
@patch('insights.client.config.get_rhel_version', return_value=10)
@patch('insights.client.config.get_egg_version_tuple', return_value=(3, 6, 10))
def test_validate_obfuscation_options_conflict_old_warning(egg, rhel, logger):
    with pytest.raises(ValueError) as ve:
        InsightsConfig(obfuscate=False, obfuscate_hostname=True, _print_errors=True)
    assert 'Option `obfuscate_hostname` requires `obfuscate`' in str(ve.value)
    logger.warning.assert_called_once_with(
        'WARNING: `obfuscate` and `obfuscate_hostname` are deprecated, please use `obfuscation_list` instead.'
    )


@patch('insights.client.config.logger')
@patch('insights.client.config.get_rhel_version', return_value=10)
@patch('insights.client.config.get_egg_version_tuple', return_value=(3, 5, 10))
def test_validate_obfuscation_options_conflict_old_no_warning(egg, rhel, logger):
    InsightsConfig(obfuscate=True, obfuscate_hostname=True, _print_errors=True)
    logger.warning.assert_not_called()


@patch('insights.client.config.logger')
@patch('insights.client.config.get_rhel_version', return_value=7)
@patch('insights.client.config.get_egg_version_tuple', return_value=(3, 6, 12))
def test_validate_obfuscation_options_conflict_old_rhel7(egg, rhel, logger):
    with pytest.raises(ValueError) as ve:
        InsightsConfig(obfuscate=False, obfuscate_hostname=True, _print_errors=True)
    assert 'Option `obfuscate_hostname` requires `obfuscate`' in str(ve.value)
    logger.warning.assert_not_called()


@pytest.mark.parametrize(
    ("obfuscate", "obfuscate_hostname", "obfuscation_list", "expected_opt"),
    [
        (True, True, '', []),
        (True, False, '', []),
        (False, False, '', []),
        (True, True, 'ipv6, hostname, ipv4', ['hostname', 'ipv4', 'ipv6']),
        (False, False, 'ipv4,ipv6,hostname,mac', ['hostname', 'ipv4', 'ipv6', 'mac']),
    ],
)
@patch('insights.client.config.logger')
@patch('insights.client.config.get_rhel_version', return_value=10)
def test_validate_obfuscation_options_conflict_new(
    rhel, logger, obfuscate, obfuscate_hostname, obfuscation_list, expected_opt
):
    c = InsightsConfig(
        obfuscate=obfuscate,
        obfuscate_hostname=obfuscate_hostname,
        obfuscation_list=obfuscation_list,
        _print_errors=True,
    )
    assert c.obfuscation_list == expected_opt
    logger.warning.assert_called_once_with(
        'WARNING: Conflicting options: `obfuscation_list` and `obfuscate`, using: "obfuscation_list={0}".'.format(
            obfuscation_list
        )
    )


@patch('insights.client.config.logger')
def test_validate_obfuscation_options_new_invalid(logger):
    c = InsightsConfig(obfuscation_list='mac, abc, ipv4', _print_errors=True)
    assert c.obfuscation_list == ['ipv4', 'mac']
    logger.warning.assert_called_once_with(
        'WARNING: ignoring invalid obfuscate options: `abc`, using: "obfuscation_list=ipv4,mac".'
    )
