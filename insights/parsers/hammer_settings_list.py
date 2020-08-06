"""
HammerSettingsList - command ``hammer --interactive 0 --output json settings list``
===================================================================================

This module provides the parser class ``HammerSettingsList`` which parses the
settings gathered using hammer tool in json format from a satellite/foreman
server.
"""
from insights import parser, JSONParser, CommandParser
from insights.specs import Specs


@parser(Specs.hammer_settings_list)
class HammerSettingsList(CommandParser, JSONParser):
    """
    Parses satellite/foreman settings gathered using hammer tool in json format.

    Sample input data::

        [
            {
                "Name": "unregister_delete_host",
                "Full name": "Delete Host upon unregister",
                "Value": "false",
                "Description": "When unregistering a host via subscription-manager, also delete the host record. Managed resources linked to host such as virtual machines and DNS records may also be deleted."
            },
            {
                "Name": "destroy_vm_on_host_delete",
                "Full name": "Destroy associated VM on host delete",
                "Value": "true",
                "Description": "Destroy associated VM on host delete. When enabled, VMs linked to Hosts will be deleted on Compute Resource. When disabled, VMs are unlinked when the host is deleted, meaning they remain on Compute Resource and can be re-associated or imported back to Foreman again. This does not automatically power off the VM"
            }
        ]

    Examples:
        >>> type(settings_list)
        <class 'insights.parsers.hammer_settings_list.HammerSettingsList'>
        >>> settings_list.data == {'unregister_delete_host': 'false', 'destroy_vm_on_host_delete': 'true'}
        True
        >>> 'unregister_delete_host' in settings_list
        True
        >>> settings_list['unregister_delete_host'] == 'false'
        True
    """
    def __init__(self, context):
        super(HammerSettingsList, self).__init__(context)
        self.data = {setting['Name']: setting['Value'] for setting in self.data}
