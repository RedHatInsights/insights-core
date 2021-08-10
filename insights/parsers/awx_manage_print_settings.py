"""
AwxManagePrintSettings - command ``awx-manage print_settings``
==============================================================
The AwxManagePrintSettings class parses the command ``awx-manage print_settings``
"""
from insights import JSONParser, parser, CommandParser
from insights.specs import Specs


@parser(Specs.awx_manage_print_settings)
class AwxManagePrintSettings(CommandParser, JSONParser):
    """
    The AwxManagePrintSettings class parses the command ``awx-manage print_settings``.

    Sample ``awx-manage print_settings INSIGHTS_TRACKING_STATE SYSTEM_UUID INSTALL_UUID TOWER_URL_BASE AWX_CLEANUP_PATHS AWX_PROOT_BASE_PATH --format json`` file::

        {
            "AWX_CLEANUP_PATHS": false,
            "AWX_PROOT_BASE_PATH": "/opt/tmp",
            "INSIGHTS_TRACKING_STATE": true,
            "INSTALL_UUID": "c0d38a6a-4449-4e13-a64b-00e0248ad229",
            "SYSTEM_UUID": "eecfd8dc-5028-46ef-9868-86f7d595da13",
            "TOWER_URL_BASE": "https://10.72.37.79"
        }

    Examples::
        >>> type(settings)
        <class 'insights.parsers.awx_manage_print_settings.AwxManagePrintSettings'>
        >>> settings['AWX_CLEANUP_PATHS']
        False
        >>> settings['SYSTEM_UUID']
        u'eecfd8dc-5028-46ef-9868-86f7d595da13'
    """
    pass
