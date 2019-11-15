# -*- coding: utf-8 -*-
# Per PEP 263
import doctest
from insights.tests import context_wrap
from insights.parsers.systemd import unitfiles
from insights.parsers.systemd.unitfiles import UnitFiles, ListUnits

KDUMP_DISABLED_RHEL7 = """
UNIT FILE                                   STATE
kdump.service                               disabled
""".strip()

KDUMP_ENABLED_RHEL7 = """
UNIT FILE                                   STATE
kdump.service                               enabled
""".strip()

KDUMP_ENABLED_FOOTER_RHEL7 = """
UNIT FILE                                   STATE
kdump.service                               enabled
1 unit file listed.
""".strip()

KDUMP_BIG_TEST = """
UNIT FILE                                   STATE
kdump.service                               enabled
other.service                               disabled
test.service                                static

3 unit files listed.
""".strip()

UNIT_INVALID_VS_VALID = """
UNIT FILE                                   STATE
svca.service                                enabled
svcb.service                                masked
svcc.service                                somenonsense

3 unit files listed.
"""


def test_unitfiles():
    context = context_wrap(KDUMP_DISABLED_RHEL7)
    unitfiles = UnitFiles(context)
    assert not unitfiles.is_on('kdump.service')
    assert len(unitfiles.services) == 1
    assert len(unitfiles.parsed_lines) == 1

    context = context_wrap(KDUMP_ENABLED_RHEL7)
    unitfiles = UnitFiles(context)
    assert unitfiles.is_on('kdump.service')
    assert len(unitfiles.services) == 1
    assert len(unitfiles.parsed_lines) == 1

    context = context_wrap(KDUMP_ENABLED_RHEL7)
    unitfiles = UnitFiles(context)
    assert unitfiles.is_on('kdump.service')
    assert len(unitfiles.services) == 1
    assert len(unitfiles.parsed_lines) == 1

    context = context_wrap(KDUMP_BIG_TEST)
    unitfiles = UnitFiles(context)
    assert unitfiles.is_on('kdump.service')
    assert not unitfiles.is_on('other.service')
    assert unitfiles.is_on('test.service')
    assert len(unitfiles.services) == 3
    assert len(unitfiles.parsed_lines) == 3

    context = context_wrap(UNIT_INVALID_VS_VALID)
    unitfiles = UnitFiles(context)
    assert unitfiles.is_on('svca.service')
    assert 'svca.service' in unitfiles.services
    assert 'svca.service' in unitfiles.service_list
    assert 'svcb.service' in unitfiles.services
    assert 'svcb.service' in unitfiles.service_list
    assert 'svcc.service' not in unitfiles.services
    assert 'svcc.service' not in unitfiles.service_list
    assert True is unitfiles.is_on('svca.service')
    assert False is unitfiles.is_on('svcb.service')
    assert None is unitfiles.is_on('svcc.service')
    assert unitfiles.exists('svca.service')
    assert unitfiles.exists('svcb.service')
    assert not unitfiles.exists('svcc.service')


LISTUNITS_CONTENT = u"""
  proc-sys-fs-binfmt_misc.automount                                           loaded active waiting   Arbitrary Executable File Formats File System Automount Point
  sys-devices-pci0000:00-0000:00:03.0-virtio0-net-eth0.device                 loaded active plugged   Virtio network device
  sys-devices-pci0000:00-0000:00:04.0-virtio1-net-eth1.device                 loaded active plugged   Virtio network device
  sys-devices-pci0000:00-0000:00:05.0-virtio2-net-eth2.device                 loaded active plugged   Virtio network device
  sys-devices-pci0000:00-0000:00:07.0-virtio3-virtio\x2dports-vport3p1.device loaded active plugged   /sys/devices/pci0000:00/0000:00:07.0/virtio3/virtio-ports/vport3p1
  sys-devices-pci0000:00-0000:00:08.0-virtio4-block-vda-vda1.device           loaded active plugged   /sys/devices/pci0000:00/0000:00:08.0/virtio4/block/vda/vda1
  sys-devices-pci0000:00-0000:00:08.0-virtio4-block-vda.device                loaded active plugged   /sys/devices/pci0000:00/0000:00:08.0/virtio4/block/vda
  sys-devices-platform-serial8250-tty-ttyS1.device                            loaded active plugged   /sys/devices/platform/serial8250/tty/ttyS1
  sys-devices-platform-serial8250-tty-ttyS2.device                            loaded active plugged   /sys/devices/platform/serial8250/tty/ttyS2
  sys-devices-platform-serial8250-tty-ttyS3.device                            loaded active plugged   /sys/devices/platform/serial8250/tty/ttyS3
  sys-devices-pnp0-00:04-tty-ttyS0.device                                     loaded active plugged   /sys/devices/pnp0/00:04/tty/ttyS0
  sys-devices-virtual-block-dm\x2d0.device                                    loaded active plugged   /sys/devices/virtual/block/dm-0
  sys-devices-virtual-block-loop0.device                                      loaded active plugged   /sys/devices/virtual/block/loop0
  sys-devices-virtual-block-loop1.device                                      loaded active plugged   /sys/devices/virtual/block/loop1
  sys-devices-virtual-net-br\x2dctlplane.device                               loaded active plugged   /sys/devices/virtual/net/br-ctlplane
  sys-devices-virtual-net-br\x2dint.device                                    loaded active plugged   /sys/devices/virtual/net/br-int
  sys-devices-virtual-net-docker0.device                                      loaded active plugged   /sys/devices/virtual/net/docker0
  sys-devices-virtual-net-eth1.905.device                                     loaded active plugged   /sys/devices/virtual/net/eth1.905
  sys-devices-virtual-net-ovs\x2dsystem.device                                loaded active plugged   /sys/devices/virtual/net/ovs-system
  sys-module-configfs.device                                                  loaded active plugged   /sys/module/configfs
  sys-subsystem-net-devices-br\x2dctlplane.device                             loaded active plugged   /sys/subsystem/net/devices/br-ctlplane
  sys-subsystem-net-devices-br\x2dint.device                                  loaded active plugged   /sys/subsystem/net/devices/br-int
  sys-subsystem-net-devices-docker0.device                                    loaded active plugged   /sys/subsystem/net/devices/docker0
  sys-subsystem-net-devices-eth0.device                                       loaded active plugged   Virtio network device
  sys-subsystem-net-devices-eth1.905.device                                   loaded active plugged   /sys/subsystem/net/devices/eth1.905
  sys-subsystem-net-devices-eth1.device                                       loaded active plugged   Virtio network device
  sys-subsystem-net-devices-eth2.device                                       loaded active plugged   Virtio network device
  sys-subsystem-net-devices-ovs\x2dsystem.device                              loaded active plugged   /sys/subsystem/net/devices/ovs-system
  -.mount                                                                     loaded active mounted   /
  dev-hugepages.mount                                                         loaded active mounted   Huge Pages File System
  dev-mqueue.mount                                                            loaded active mounted   POSIX Message Queue File System
  proc-fs-nfsd.mount                                                          loaded active mounted   NFSD configuration filesystem
  run-netns.mount                                                             loaded active mounted   /run/netns
  run-user-0.mount                                                            loaded active mounted   /run/user/0
  sys-kernel-config.mount                                                     loaded active mounted   Configuration File System
  sys-kernel-debug.mount                                                      loaded active mounted   Debug File System
  var-lib-nfs-rpc_pipefs.mount                                                loaded active mounted   RPC Pipe File System
  brandbot.path                                                               loaded active waiting   Flexible branding
  systemd-ask-password-console.path                                           loaded active waiting   Dispatch Password Requests to Console Directory Watch
  systemd-ask-password-wall.path                                              loaded active waiting   Forward Password Requests to Wall Directory Watch
  session-97.scope                                                            loaded active running   Session 97 of user root
  atd.service                                                                 loaded active running   Job spooling tools
  auditd.service                                                              loaded active running   Security Auditing Service
  bootif-fix.service                                                          loaded active running   Automated fix for incorrect iPXE BOOFIF
  chronyd.service                                                             loaded active running   NTP client/server
  crond.service                                                               loaded active running   Command Scheduler
  dbus.service                                                                loaded active running   D-Bus System Message Bus
  dnsmasq.service                                                             loaded active running   DNS caching server.
  docker-distribution.service                                                 loaded active running   v2 Registry server for Docker
● docker-storage-setup.service                                                loaded failed failed    Docker Storage Setup
  docker.service                                                              loaded active running   Docker Application Container Engine
  epmd@0.0.0.0.service                                                        loaded active running   Erlang Port Mapper Daemon
  getty@tty1.service                                                          loaded active running   Getty on tty1
  gssproxy.service                                                            loaded active running   GSSAPI Proxy Daemon
  httpd.service                                                               loaded active running   The Apache HTTP Server
  iptables.service                                                            loaded active exited    IPv4 firewall with iptables
  ipxe-timeout-fix.service                                                    loaded active running   Automated fix for incorrect iPXE timeout
  ironicapi-fix.service                                                       loaded active running   Automated fix to restart ironic-api when it crashes
  irqbalance.service                                                          loaded active running   irqbalance daemon
  iscsi-shutdown.service                                                      loaded active exited    Logout off all iSCSI sessions on shutdown
  iscsid.service                                                              loaded active running   Open-iSCSI
  kdump.service                                                               loaded active exited    Crash recovery kernel arming
  kmod-static-nodes.service                                                   loaded active exited    Create list of required static device nodes for the current kernel
  ksm.service                                                                 loaded active exited    Kernel Samepage Merging
  ksmtuned.service                                                            loaded active running   Kernel Samepage Merging (KSM) Tuning Daemon
  libvirtd.service                                                            loaded active running   Virtualization daemon
  lvm2-lvmetad.service                                                        loaded active running   LVM2 metadata daemon
  lvm2-monitor.service                                                        loaded active exited    Monitoring of LVM2 mirrors, snapshots etc. using dmeventd or progress polling
  mariadb.service                                                             loaded active running   MariaDB database server
  memcached.service                                                           loaded active running   memcached daemon
  mongod.service                                                              loaded active running   High-performance, schema-free document-oriented database
  netcf-transaction.service                                                   loaded active exited    Rollback uncommitted netcf network config change transactions
  network.service                                                             loaded active exited    LSB: Bring up/down networking
● NetworkManager-wait-online.service                                          loaded failed failed    Network Manager Wait Online
  NetworkManager.service                                                      loaded active running   Network Manager
  neutron-dhcp-agent.service                                                  loaded active running   OpenStack Neutron DHCP Agent
  neutron-openvswitch-agent.service                                           loaded active running   OpenStack Neutron Open vSwitch Agent
  neutron-ovs-cleanup.service                                                 loaded active exited    OpenStack Neutron Open vSwitch Cleanup Utility
  neutron-server.service                                                      loaded active running   OpenStack Neutron Server
  openstack-aodh-evaluator.service                                            loaded active running   OpenStack Alarm evaluator service
  openstack-aodh-listener.service                                             loaded active running   OpenStack Alarm listener service
  openstack-aodh-notifier.service                                             loaded active running   OpenStack Alarm notifier service
  openstack-ceilometer-central.service                                        loaded active running   OpenStack ceilometer central agent
  openstack-ceilometer-collector.service                                      loaded active running   OpenStack ceilometer collection service
  openstack-ceilometer-notification.service                                   loaded active running   OpenStack ceilometer notification agent
  openstack-glance-api.service                                                loaded active running   OpenStack Image Service (code-named Glance) API server
  openstack-glance-registry.service                                           loaded active running   OpenStack Image Service (code-named Glance) Registry server
  openstack-heat-api-cfn.service                                              loaded active running   Openstack Heat CFN-compatible API Service
  openstack-heat-api.service                                                  loaded active running   OpenStack Heat API Service
  openstack-heat-engine.service                                               loaded active running   Openstack Heat Engine Service
  openstack-ironic-api.service                                                loaded active running   OpenStack Ironic API service
  openstack-ironic-conductor.service                                          loaded active running   OpenStack Ironic Conductor service
  openstack-ironic-inspector-dnsmasq.service                                  loaded active running   PXE boot dnsmasq service for Ironic Inspector
  openstack-ironic-inspector.service                                          loaded active running   Hardware introspection service for OpenStack Ironic
  openstack-mistral-api.service                                               loaded active running   Mistral API Server
  openstack-mistral-engine.service                                            loaded active running   Mistral Engine Server
  openstack-mistral-executor.service                                          loaded active running   Mistral Executor Server
  openstack-nova-api.service                                                  loaded active running   OpenStack Nova API Server
  openstack-nova-cert.service                                                 loaded active running   OpenStack Nova Cert Server
  openstack-nova-compute.service                                              loaded active running   OpenStack Nova Compute Server
  openstack-nova-conductor.service                                            loaded active running   OpenStack Nova Conductor Server
  openstack-nova-scheduler.service                                            loaded active running   OpenStack Nova Scheduler Server
  openstack-swift-account-reaper.service                                      loaded active running   OpenStack Object Storage (swift) - Account Reaper
  openstack-swift-account.service                                             loaded active running   OpenStack Object Storage (swift) - Account Server
  openstack-swift-container-updater.service                                   loaded active running   OpenStack Object Storage (swift) - Container Updater
  openstack-swift-container.service                                           loaded active running   OpenStack Object Storage (swift) - Container Server
  openstack-swift-object-updater.service                                      loaded active running   OpenStack Object Storage (swift) - Object Updater
  openstack-swift-object.service                                              loaded active running   OpenStack Object Storage (swift) - Object Server
  openstack-swift-proxy.service                                               loaded active running   OpenStack Object Storage (swift) - Proxy Server
  openstack-zaqar.service                                                     loaded active running   OpenStack Message Queuing Service (code-named Zaqar) Server
  openstack-zaqar@1.service                                                   loaded active running   OpenStack Message Queuing Service (code-named Zaqar) Server Instance 1
  openvswitch.service                                                         loaded active exited    Open vSwitch
● ovirt-guest-agent.service                                                   loaded failed failed    oVirt Guest Agent
  ovs-vswitchd.service                                                        loaded active running   Open vSwitch Forwarding Unit
  ovsdb-server.service                                                        loaded active running   Open vSwitch Database Unit
  polkit.service                                                              loaded active running   Authorization Manager
  postfix.service                                                             loaded active running   Postfix Mail Transport Agent
  qemu-guest-agent.service                                                    loaded active running   QEMU Guest Agent
  rabbitmq-server.service                                                     loaded active running   RabbitMQ broker
  rc-local.service                                                            loaded active exited    /etc/rc.d/rc.local Compatibility
  rhel-dmesg.service                                                          loaded active exited    Dump dmesg to /var/log/dmesg
  rhel-import-state.service                                                   loaded active exited    Import network configuration from initramfs
  rhel-push-plugin.service                                                    loaded active running   Docker Block RHEL push plugin authZ Plugin
  rhel-readonly.service                                                       loaded active exited    Configure read-only root support
  rhnsd.service                                                               loaded active running   LSB: Starts the Spacewalk Daemon
  rsyslog.service                                                             loaded active running   System Logging Service
  serial-getty@ttyS0.service                                                  loaded active running   Serial Getty on ttyS0
  sshd.service                                                                loaded active running   OpenSSH server daemon
  systemd-journal-flush.service                                               loaded active exited    Flush Journal to Persistent Storage
  systemd-journald.service                                                    loaded active running   Journal Service
  systemd-logind.service                                                      loaded active running   Login Service
  systemd-random-seed.service                                                 loaded active exited    Load/Save Random Seed
  systemd-remount-fs.service                                                  loaded active exited    Remount Root and Kernel File Systems
  systemd-sysctl.service                                                      loaded active exited    Apply Kernel Variables
  systemd-tmpfiles-setup-dev.service                                          loaded active exited    Create Static Device Nodes in /dev
  systemd-tmpfiles-setup.service                                              loaded active exited    Create Volatile Files and Directories
  systemd-udev-trigger.service                                                loaded active exited    udev Coldplug all Devices
  systemd-udevd.service                                                       loaded active running   udev Kernel Device Manager
  systemd-update-utmp.service                                                 loaded active exited    Update UTMP about System Boot/Shutdown
  systemd-user-sessions.service                                               loaded active exited    Permit User Sessions
  systemd-vconsole-setup.service                                              loaded active exited    Setup Virtual Console
  tuned.service                                                               loaded active running   Dynamic System Tuning Daemon
  xinetd.service                                                              loaded active running   Xinetd A Powerful Replacement For Inetd
  -.slice                                                                     loaded active active    Root Slice
  system-epmd.slice                                                           loaded active active    system-epmd.slice
  system-getty.slice                                                          loaded active active    system-getty.slice
  system-openstack\x2dzaqar.slice                                             loaded active active    system-openstack\x2dzaqar.slice
  system-selinux\x2dpolicy\x2dmigrate\x2dlocal\x2dchanges.slice               loaded active active    system-selinux\x2dpolicy\x2dmigrate\x2dlocal\x2dchanges.slice
  system-serial\x2dgetty.slice                                                loaded active active    system-serial\x2dgetty.slice
  system.slice                                                                loaded active active    System Slice
  user-0.slice                                                                loaded active active    user-0.slice
  user.slice                                                                  loaded active active    User and Session Slice
  dbus.socket                                                                 loaded active running   D-Bus System Message Bus Socket
  dm-event.socket                                                             loaded active listening Device-mapper event daemon FIFOs
  epmd@0.0.0.0.socket                                                         loaded active running   Erlang Port Mapper Daemon Activation Socket
  iscsid.socket                                                               loaded active running   Open-iSCSI iscsid Socket
  iscsiuio.socket                                                             loaded active listening Open-iSCSI iscsiuio Socket
  lvm2-lvmetad.socket                                                         loaded active running   LVM2 metadata daemon socket
  lvm2-lvmpolld.socket                                                        loaded active listening LVM2 poll daemon socket
  rhel-push-plugin.socket                                                     loaded active running   Docker Block RHEL push plugin Socket for the API
  rpcbind.socket                                                              loaded active listening RPCbind Server Activation Socket
  systemd-initctl.socket                                                      loaded active listening /dev/initctl Compatibility Named Pipe
  systemd-journald.socket                                                     loaded active running   Journal Socket
  systemd-shutdownd.socket                                                    loaded active listening Delayed Shutdown Socket
  systemd-udevd-control.socket                                                loaded active running   udev Control Socket
  systemd-udevd-kernel.socket                                                 loaded active running   udev Kernel Socket
  virtlockd.socket                                                            loaded active listening Virtual machine lock manager socket
  virtlogd.socket                                                             loaded active listening Virtual machine log manager socket
  swap.file.swap                                                              loaded active active    /swap.file
  basic.target                                                                loaded active active    Basic System
  cryptsetup.target                                                           loaded active active    Encrypted Volumes
  getty.target                                                                loaded active active    Login Prompts
  local-fs-pre.target                                                         loaded active active    Local File Systems (Pre)
  local-fs.target                                                             loaded active active    Local File Systems
  multi-user.target                                                           loaded active active    Multi-User System
  network-online.target                                                       loaded active active    Network is Online
  network.target                                                              loaded active active    Network
  nfs-client.target                                                           loaded active active    NFS client services
  paths.target                                                                loaded active active    Paths
  remote-fs-pre.target                                                        loaded active active    Remote File Systems (Pre)
  remote-fs.target                                                            loaded active active    Remote File Systems
  slices.target                                                               loaded active active    Slices
  sockets.target                                                              loaded active active    Sockets
  swap.target                                                                 loaded active active    Swap
  sysinit.target                                                              loaded active active    System Initialization
  timers.target                                                               loaded active active    Timers
  docker-cleanup.timer                                                        loaded active waiting   Run docker-cleanup every hour
  systemd-tmpfiles-clean.timer                                                loaded active waiting   Daily Cleanup of Temporary Directories
  unbound-anchor.timer                                                        loaded active waiting   daily update of the root trust anchor for DNSSEC
* openstack-swift-proxy.service                                               loaded failed failed    OpenStack Object Storage (swift) - Proxy Server

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

189 loaded units listed. Pass --all to see loaded but inactive units, too.
To show all installed unit files use 'systemctl list-unit-files'.
""".strip()

LISTUNITS_CONTENT_2 = """
sockets.target                                                              loaded active active    Sockets
swap.target                                                                 loaded active active    Swap
systemd-shutdownd.socket                                                    loaded active listening Delayed Shutdown Socket
neutron-dhcp-agent.service                                                  loaded active running   OpenStack Neutron DHCP     Agent
neutron-openvswitch-agent.service                                           loaded active running   OpenStack Neutron Open     vSwitch Agent
chronyd.service                                                             loaded failed failed    NTP client/server
""".strip()


def test_listunits():
    context = context_wrap(LISTUNITS_CONTENT)
    list_units = ListUnits(context)
    service_name = "neutron-dhcp-agent.service"
    service_details = list_units.get_service_details(service_name)
    assert list_units.is_running(service_name) is True
    assert list_units.is_failed(service_name) is False
    assert service_details['UNIT'] == "neutron-dhcp-agent.service"
    service_name = "virtlogd.socket"
    service_details = list_units.get_service_details(service_name)
    assert service_details['SUB'] == "listening"
    service_name = "NetworkManager-wait-online.service"
    service_details = list_units.get_service_details(service_name)
    assert service_details['SUB'] == "failed"
    service_name = "ovirt-guest-agent.service"
    service_details = list_units.get_service_details(service_name)
    assert service_details['ACTIVE'] == "failed"
    service_name = "docker-storage-setup.service"
    assert list_units.is_running(service_name) is False
    assert list_units.is_failed(service_name) is True
    service_name = "openstack-swift-proxy.service"
    service_details = list_units.get_service_details(service_name)
    assert service_details['SUB'] == "failed"

    context = context_wrap(LISTUNITS_CONTENT_2)
    list_units = ListUnits(context)
    service_name = "systemd-shutdownd.socket"
    assert list_units.is_active(service_name) is True
    assert list_units.is_running(service_name) is False
    service_details = list_units.get_service_details(service_name)
    assert service_details['UNIT'] == "systemd-shutdownd.socket"
    service_name = "random.service"
    service_details = list_units.get_service_details(service_name)
    assert service_details['ACTIVE'] is None
    service_name = "chronyd.service"
    assert list_units.is_active(service_name) is False
    assert list_units.is_failed(service_name) is True


LISTUNITS_CONTENT_3 = u"""
UNIT                                                                                LOAD   ACTIVE SUB       DESCRIPTION
proc-sys-fs-binfmt_misc.automount                                                   loaded active waiting   Arbitrary Executable File Formats File System Automount Point
sys-devices-pci0000:00-0000:00:01.1-ata1-host0-target0:0:0-0:0:0:0-block-sr0.device loaded active plugged   QEMU_DVD-ROM
sys-devices-pci0000:00-0000:00:03.0-virtio0-net-eth0.device                         loaded active plugged   Virtio network device
sys-devices-pci0000:00-0000:00:04.0-sound-card0.device                              loaded active plugged   82801FB/FBM/FR/FW/FRW (ICH6 Family) High Definition Audio Controller (QEMU Virtual Machine)
sys-devices-pci0000:00-0000:00:06.0-virtio1-virtio\x2dports-vport1p1.device         loaded active plugged   /sys/devices/pci0000:00/0000:00:06.0/virtio1/virtio-ports/vport1p1
sys-devices-pci0000:00-0000:00:06.0-virtio1-virtio\x2dports-vport1p2.device         loaded active plugged   /sys/devices/pci0000:00/0000:00:06.0/virtio1/virtio-ports/vport1p2
sys-devices-pci0000:00-0000:00:07.0-virtio2-block-vda-vda1.device                   loaded active plugged   /sys/devices/pci0000:00/0000:00:07.0/virtio2/block/vda/vda1
sys-devices-pci0000:00-0000:00:07.0-virtio2-block-vda-vda2.device                   loaded active plugged   LVM PV m1dNfE-0R8d-dbBp-n4F9-mT11-dffC-M4S0wq on /dev/vda2 2
sys-devices-pci0000:00-0000:00:07.0-virtio2-block-vda.device                        loaded active plugged   /sys/devices/pci0000:00/0000:00:07.0/virtio2/block/vda
insights-client.timer                                                               loaded active waiting   Insights Client Timer Task
systemd-tmpfiles-clean.timer                                                        loaded active waiting   Daily Cleanup of Temporary Directories
unbound-anchor.timer                                                                loaded active waiting   daily update of the root trust anchor for DNSSEC

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

161 loaded units listed. Pass --all to see loaded but inactive units, too.
To show all installed unit files use 'systemctl list-unit-files'.
""".strip()


def test_listunits_headings():
    list_units = ListUnits(context_wrap(LISTUNITS_CONTENT_3))
    assert set(list_units.service_names) == set([
        'proc-sys-fs-binfmt_misc.automount',
        'sys-devices-pci0000:00-0000:00:01.1-ata1-host0-target0:0:0-0:0:0:0-block-sr0.device',
        'sys-devices-pci0000:00-0000:00:03.0-virtio0-net-eth0.device',
        'sys-devices-pci0000:00-0000:00:04.0-sound-card0.device',
        u'sys-devices-pci0000:00-0000:00:06.0-virtio1-virtio\x2dports-vport1p1.device',
        u'sys-devices-pci0000:00-0000:00:06.0-virtio1-virtio\x2dports-vport1p2.device',
        'sys-devices-pci0000:00-0000:00:07.0-virtio2-block-vda-vda1.device',
        'sys-devices-pci0000:00-0000:00:07.0-virtio2-block-vda-vda2.device',
        'sys-devices-pci0000:00-0000:00:07.0-virtio2-block-vda.device',
        'insights-client.timer',
        'systemd-tmpfiles-clean.timer',
        'unbound-anchor.timer'
    ])
    assert list_units.get_service_details('insights-client.timer')['DESCRIPTION'] == 'Insights Client Timer Task'


LISTUNITS_DOCTEST = """
UNIT                                LOAD   ACTIVE SUB       DESCRIPTION
sockets.target                      loaded active active    Sockets
swap.target                         loaded active active    Swap
systemd-shutdownd.socket            loaded active listening Delayed Shutdown Socket
neutron-dhcp-agent.service          loaded active running   OpenStack Neutron DHCP Agent
neutron-openvswitch-agent.service   loaded active running   OpenStack Neutron Open vSwitch Agent
...
unbound-anchor.timer                loaded active waiting   daily update of the root trust anchor for DNSSEC

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

161 loaded units listed. Pass --all to see loaded but inactive units, too.
To show all installed unit files use 'systemctl list-unit-files'.
""".strip()


UNITFILES_DOCTEST = """
UNIT FILE                                     STATE
mariadb.service                               enabled
neutron-openvswitch-agent.service             enabled
neutron-ovs-cleanup.service                   enabled
neutron-server.service                        enabled
runlevel0.target                              disabled
runlevel1.target                              disabled
runlevel2.target                              enabled
""".strip()


def test_unitfiles_doc_examples():
    env = {
        'conf': UnitFiles(context_wrap(UNITFILES_DOCTEST)),
        'units': ListUnits(context_wrap(LISTUNITS_DOCTEST)),
    }
    failed, total = doctest.testmod(unitfiles, globs=env)
    assert failed == 0
