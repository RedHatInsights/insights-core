import doctest
import pytest
from insights.parsers import SkipException
from ...parsers import subscription_manager_list
from ...tests import context_wrap


subscription_manager_list_consumed_in_docs = '''
+-------------------------------------------+
   Consumed Subscriptions
+-------------------------------------------+
Subscription Name: Red Hat Enterprise Linux Server, Premium (1-2 sockets) (Up to 1 guest)
Provides:          Oracle Java (for RHEL Server)
                   Red Hat Software Collections Beta (for RHEL Server)
                   Red Hat Enterprise Linux Server
                   Red Hat Beta
SKU:               RH0155783S
Contract:          12345678
Account:           1000001
Serial:            0102030405060708090
Pool ID:           8a85f981477e5284014783abaf5d4dcd
Active:            True
Quantity Used:     1
Service Level:     PREMIUM
Service Type:      L1-L3
Status Details:    Subscription is current
Subscription Type: Standard
Starts:            11/14/14
Ends:              07/06/15
System Type:       Physical
'''

subscription_manager_list_installed_in_docs = '''
+-------------------------------------------+
Installed Product Status
+-------------------------------------------+
Product Name:   Red Hat Software Collections (for RHEL Server)
Product ID:     201
Version:        2
Arch:           x86_64
Status:         Subscribed
Status Details:
Starts:         04/27/15
Ends:           04/27/16

Product Name:   Red Hat Enterprise Linux Server
Product ID:     69
Version:        7.1
Arch:           x86_64
Status:         Subscribed
Status Details:
Starts:         04/27/15
Ends:           04/27/16
'''

subscription_manager_repos_list_enabled_test_data = '''
+----------------------------------------------------------+
    Available Repositories in /etc/yum.repos.d/redhat.repo
+----------------------------------------------------------+
Repo ID:   rhel-7-server-ansible-2-rpms
Repo Name: Red Hat Ansible Engine 2 RPMs for Red Hat Enterprise Linux 7 Server
Repo URL:  https://cdn.redhat.com/content/dist/rhel/server/7/7Server/$basearch/ansible/2/os
Enabled:   1
'''

FACTS_LIST = """
cpu.core(s)_per_socket: 2
cpu.cpu(s): 2
cpu.cpu_socket(s): 1
cpu.thread(s)_per_core: 1
cpu.topology_source: kernel /sys cpu sibling lists
distribution.id: Maipo
distribution.name: Red Hat Enterprise Linux Server
distribution.version: 7.2
distribution.version.modifier: ga
dmi.baseboard.manufacturer: Oracle Corporation
dmi.baseboard.product_name: VirtualBox
dmi.baseboard.serial_number: 0
dmi.baseboard.version: 1.2
dmi.bios.address: 0xe0000
dmi.bios.relase_date: 12/01/2006
dmi.bios.rom_size: 128 KB
dmi.bios.runtime_size: 128 KB
dmi.bios.vendor: innotek GmbH
dmi.bios.version: VirtualBox
dmi.chassis.asset_tag: Not Specified
dmi.chassis.boot-up_state: Safe
dmi.chassis.lock: Not Present
dmi.chassis.manufacturer: Oracle Corporation
dmi.chassis.power_supply_state: Safe
dmi.chassis.security_status: None
dmi.chassis.serial_number: Not Specified
dmi.chassis.thermal_state: Safe
dmi.chassis.type: Other
dmi.chassis.version: Not Specified
dmi.system.family: Virtual Machine
dmi.system.manufacturer: innotek GmbH
dmi.system.product_name: VirtualBox
dmi.system.serial_number: 0
dmi.system.sku_number: Not Specified
dmi.system.uuid: e81897b5-94df-4979-a8e2-b496756b5cbc
dmi.system.version: 1.2
dmi.system.wake-up_type: Power Switch
lscpu.architecture: x86_64
lscpu.bogomips: 5587.10
lscpu.byte_order: Little Endian
lscpu.core(s)_per_socket: 2
lscpu.cpu(s): 2
lscpu.cpu_family: 6
lscpu.cpu_mhz: 2793.550
lscpu.cpu_op-mode(s): 32-bit, 64-bit
lscpu.hypervisor_vendor: KVM
lscpu.l1d_cache: 32K
lscpu.l1i_cache: 32K
lscpu.l2_cache: 256K
lscpu.l3_cache: 6144K
lscpu.model: 60
lscpu.model_name: Intel(R) Core(TM) i7-4810MQ CPU @ 2.80GHz
lscpu.numa_node(s): 1
lscpu.numa_node0_cpu(s): 0,1
lscpu.on-line_cpu(s)_list: 0,1
lscpu.socket(s): 1
lscpu.stepping: 3
lscpu.thread(s)_per_core: 1
lscpu.vendor_id: GenuineIntel
lscpu.virtualization_type: full
memory.memtotal: 1884064
memory.swaptotal: 520188
net.interface.enp0s3.ipv4_address: 10.0.2.15
net.interface.enp0s3.ipv4_broadcast: 10.0.2.255
net.interface.enp0s3.ipv4_netmask: 24
net.interface.enp0s3.ipv6_address.link: e80f::00:27ff:fe4a:c5efa
net.interface.enp0s3.ipv6_netmask.link: 64
net.interface.enp0s3.mac_address: AA:BB:CC:DD:EE:FF
net.interface.enp0s8.mac_address: AA:BB:CC:DD:EE:FF
net.interface.enp0s9.mac_address: AA:BB:CC:DD:EE:FF
net.interface.lo.ipv4_address: 127.0.0.1
net.interface.lo.ipv4_broadcast: Unknown
net.interface.lo.ipv4_netmask: 8
net.interface.lo.ipv6_address.host: ::1
net.interface.lo.ipv6_netmask.host: 128
network.hostname: rhel7-box
network.ipv4_address: 127.0.0.1
network.ipv6_address: ::1
system.certificate_version: 3.2
uname.machine: x86_64
uname.nodename: rhel7-box
uname.release: 3.10.0-327.el7.x86_64
uname.sysname: Linux
uname.version: #1 SMP Thu Oct 29 17:29:29 EDT 2015
virt.host_type: virtualbox, kvm
virt.is_guest: True
virt.uuid: 81897b5e-4df9-9794-8e2a-b496756b5cbc
""".strip()


subscription_manager_list_test_data = '''
+-------------------------------------------+
   Consumed Subscriptions
+-------------------------------------------+
Subscription Name: Red Hat Enterprise Linux Server, Premium (1-2 sockets) (Up to 1 guest)
Subscription Type: Standard
Starts:            17/2
'''

subscription_manager_list_no_installed_products = '''
No installed products to list
'''


def test_subscription_manager_list_exceptions():
    sml = subscription_manager_list.SubscriptionManagerListConsumed(
        context_wrap(subscription_manager_list_test_data)
    )
    assert len(sml.records) == 1
    rec0 = sml.records[0]
    assert 'Subscription Name' in rec0
    assert 'Subscription Type' in rec0
    assert 'Starts' in rec0
    assert rec0['Starts'] == '17/2'
    assert 'Starts timestamp' not in rec0

    sml = subscription_manager_list.SubscriptionManagerListInstalled(
        context_wrap(subscription_manager_list_no_installed_products)
    )
    assert sml.records == []


def test_all_facts():
    output = subscription_manager_list.SubscriptionManagerFactsList(context_wrap(FACTS_LIST))
    assert output['virt.uuid'] == '81897b5e-4df9-9794-8e2a-b496756b5cbc'
    assert output['net.interface.lo.ipv6_address.host'] == "::1"
    assert output['net.interface.enp0s9.mac_address'] == "AA:BB:CC:DD:EE:FF"
    assert output['net.interface.enp0s3.ipv6_address.link'] == "e80f::00:27ff:fe4a:c5efa"
    assert output['virt.host_type'] == "virtualbox, kvm"


def test_no_facts():
    with pytest.raises(SkipException) as ex:
        subscription_manager_list.SubscriptionManagerFactsList(context_wrap(''))
    assert "Empty content." in str(ex)


def test_subscription_manager_list_docs():
    env = {
        'repolist': subscription_manager_list.SubscriptionManagerReposListEnabled(context_wrap(subscription_manager_repos_list_enabled_test_data)),
        'installed': subscription_manager_list.SubscriptionManagerListInstalled(context_wrap(subscription_manager_list_installed_in_docs)),
        'consumed': subscription_manager_list.SubscriptionManagerListConsumed(context_wrap(subscription_manager_list_consumed_in_docs)),
        'facts': subscription_manager_list.SubscriptionManagerFactsList(context_wrap(FACTS_LIST))
    }
    failed, total = doctest.testmod(subscription_manager_list, globs=env)
    assert failed == 0
