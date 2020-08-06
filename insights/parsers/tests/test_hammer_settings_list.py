import doctest

from insights.parsers import hammer_settings_list
from insights.parsers.hammer_settings_list import HammerSettingsList
from insights.tests import context_wrap

SETTINGS_LIST_1 = """
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
""".strip()

BAD_JSON = """
[
    {
        "Name": "ansible_connection",
        "Full name": "Connection type",
        "Value": "ssh",
        "Description": "Use this connection type by default when running Ansible playbooks. You can override this on hosts by adding a parameter \"ansible_connection\""
    },
    {
        "Name": "Default_variables_Lookup_Path",
        "Full name": "Default variables lookup path",
        "Value": "[\"fqdn\", \"hostgroup\", \"os\", \"domain\"]",
        "Description": "Foreman will evaluate host smart variables in this order by default"
    }
]
""".strip()


def test_hammer_settings_list():
    settings_list = HammerSettingsList(context_wrap(SETTINGS_LIST_1))
    assert settings_list.data == {'unregister_delete_host': 'false', 'destroy_vm_on_host_delete': 'true'}
    assert ('unregister_delete_host' in settings_list) is True
    assert ('fake' in settings_list) is False
    assert settings_list['unregister_delete_host'] == 'false'

    settings_list = HammerSettingsList(context_wrap(BAD_JSON))


def test_hammer_settings_list_examples():
    env = {'settings_list': HammerSettingsList(context_wrap(SETTINGS_LIST_1))}
    failed, total = doctest.testmod(hammer_settings_list, globs=env)
    assert failed == 0
