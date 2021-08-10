import doctest
from insights.parsers import awx_manage_print_settings
from insights.tests import context_wrap

AWX_MANAGE_PRINT_SETTINGS = '''
{
    "AWX_CLEANUP_PATHS": false,
    "AWX_PROOT_BASE_PATH": "/opt/tmp",
    "INSIGHTS_TRACKING_STATE": true,
    "INSTALL_UUID": "c0d38a6a-4449-4e13-a64b-00e0248ad229",
    "SYSTEM_UUID": "eecfd8dc-5028-46ef-9868-86f7d595da13",
    "TOWER_URL_BASE": "https://10.72.37.79"
}
'''.strip()


def test_awx_manage_print_settings():
    settings = awx_manage_print_settings.AwxManagePrintSettings(context_wrap(AWX_MANAGE_PRINT_SETTINGS))
    assert not settings['AWX_CLEANUP_PATHS']
    assert settings['INSIGHTS_TRACKING_STATE']
    assert settings['SYSTEM_UUID'] == "eecfd8dc-5028-46ef-9868-86f7d595da13"


def test_awx_manage_print_settings_documentation():
    failed_count, tests = doctest.testmod(
        awx_manage_print_settings,
        globs={'settings': awx_manage_print_settings.AwxManagePrintSettings(context_wrap(AWX_MANAGE_PRINT_SETTINGS))}
    )
    assert failed_count == 0
