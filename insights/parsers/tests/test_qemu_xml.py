import doctest

from insights.parsers import qemu_xml
from insights.tests import context_wrap

XML_NUMA = """
<!--
WARNING: THIS IS AN AUTO-GENERATED FILE. CHANGES TO IT ARE LIKELY TO BE
OVERWRITTEN AND LOST. Changes to this xml configuration should be made using:
  virsh edit 05-s00c06h0
or other application using the libvirt API.
-->

<domain type='kvm'>
  <name>05-s00c06h0</name>
  <uuid>02cf0bba-2bd6-11e7-8337-e4115b9a50d0</uuid>
  <memory unit='KiB'>12582912</memory>
  <currentMemory unit='KiB'>12582912</currentMemory>
  <vcpu placement='static'>4</vcpu>
  <cputune>
    <vcpupin vcpu='0' cpuset='1'/>
    <vcpupin vcpu='1' cpuset='2'/>
    <vcpupin vcpu='2' cpuset='3'/>
    <vcpupin vcpu='3' cpuset='4'/>
    <emulatorpin cpuset='1-4'/>
  </cputune>
  <numatune>
    <memory mode='strict' nodeset='0-1'/>
    <memnode cellid='0' mode='strict' nodeset='0'/>
    <memnode cellid='1' mode='strict' nodeset='1'/>
  </numatune>
  <os>
    <type arch='x86_64' machine='pc-i440fx-rhel7.0.0'>hvm</type>
    <boot dev='hd'/>
    <boot dev='network'/>
    <bootmenu enable='yes' timeout='1000'/>
    <bios useserial='yes' rebootTimeout='0'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <cpu>
    <numa>
      <cell id='0' cpus='0-1' memory='6291456' unit='KiB'/>
      <cell id='1' cpus='2-3' memory='6291456' unit='KiB'/>
    </numa>
  </cpu>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw' cache='none' io='threads'/>
      <source file='/var/lib/libvirt/images/05-s00c06h0_1.img'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <controller type='virtio-serial' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </controller>
    <interface type='hostdev' managed='yes'>
      <mac address='aa:ss:bb:cc:dd:ee'/>
      <source>
        <address type='pci' domain='0x0000' bus='0x04' slot='0x10' function='0x0'/>
      </source>
      <rom bar='on' file='/opt/vcp/share/ipxe/808610ed.rom'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </interface>
    <interface type='hostdev' managed='yes'>
      <mac address='bb:55:77:11:00:00'/>
      <source>
        <address type='pci' domain='0x0000' bus='0x04' slot='0x10' function='0x1'/>
      </source>
      <rom bar='on' file='/opt/vcp/share/ipxe/808610ed.rom'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <channel type='pipe'>
      <source path='/var/lib/libvirt/qemu/channels/FROM-05-s00c06h0'/>
      <target type='virtio' name='virtio2host'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
    <channel type='pipe'>
      <source path='/var/lib/libvirt/qemu/channels/HGC-05-s00c06h0'/>
      <target type='virtio' name='virtio_host_guest_check'/>
      <address type='virtio-serial' controller='0' bus='0' port='2'/>
    </channel>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='vnc' port='-1' autoport='yes'>
      <listen type='address'/>
    </graphics>
    <video>
      <model type='cirrus' vram='16384' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <watchdog model='i6300esb' action='reset'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    </watchdog>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </memballoon>
  </devices>
</domain>
"""

XML_NUMA_NO_NAME = """
<!--
WARNING: THIS IS AN AUTO-GENERATED FILE. CHANGES TO IT ARE LIKELY TO BE
OVERWRITTEN AND LOST. Changes to this xml configuration should be made using:
  virsh edit 05-s00c06h0
or other application using the libvirt API.
-->

<domain type='kvm'>
  <uuid>02cf0bba-2bd6-11e7-8337-e4115b9a50d0</uuid>
  <memory unit='KiB'>12582912</memory>
</domain>
"""

BLANK_XML = """
"""

RHEL_7_4_XML = """
<!--
WARNING: THIS IS AN AUTO-GENERATED FILE. CHANGES TO IT ARE LIKELY TO BE
OVERWRITTEN AND LOST. Changes to this xml configuration should be made using:
  virsh edit rhel7.4
or other application using the libvirt API.
-->

<domain type='kvm'>
  <name>rhel7.4</name>
  <uuid>b75610eb-06a0-4834-8286-e3d25d79c593</uuid>
  <memory unit='KiB'>4194304</memory>
  <currentMemory unit='KiB'>4194304</currentMemory>
  <vcpu placement='static'>4</vcpu>
  <os>
    <type arch='x86_64' machine='pc-i440fx-2.10'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <vmport state='off'/>
  </features>
  <cpu mode='custom' match='exact' check='partial'>
    <model fallback='allow'>Haswell-noTSX</model>
  </cpu>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <pm>
    <suspend-to-mem enabled='no'/>
    <suspend-to-disk enabled='no'/>
  </pm>
  <devices>
    <emulator>/usr/bin/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='/var/lib/libvirt/images/rhel-7.4-insights.qcow2'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    </disk>
    <controller type='usb' index='0' model='ich9-ehci1'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x7'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci1'>
      <master startport='0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0' multifunction='on'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci2'>
      <master startport='2'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x1'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci3'>
      <master startport='4'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <controller type='virtio-serial' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </controller>
    <interface type='network'>
      <mac address='aa:ss:bb:ff:ee:mm'/>
      <source network='default'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <channel type='unix'>
      <target type='virtio' name='org.qemu.guest_agent.0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
    <channel type='spicevmc'>
      <target type='virtio' name='com.redhat.spice.0'/>
      <address type='virtio-serial' controller='0' bus='0' port='2'/>
    </channel>
    <input type='tablet' bus='usb'>
      <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='spice' autoport='yes'>
      <listen type='address'/>
      <image compression='off'/>
    </graphics>
    <sound model='ich6'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </sound>
    <video>
      <model type='qxl' ram='65536' vram='65536' vgamem='16384' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <redirdev bus='usb' type='spicevmc'>
      <address type='usb' bus='0' port='2'/>
    </redirdev>
    <redirdev bus='usb' type='spicevmc'>
      <address type='usb' bus='0' port='3'/>
    </redirdev>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
    </memballoon>
  </devices>
</domain>
"""

XML_IDM_CLIENT = """
<!--
WARNING: THIS IS AN AUTO-GENERATED FILE. CHANGES TO IT ARE LIKELY TO BE
OVERWRITTEN AND LOST. Changes to this xml configuration should be made using:
  virsh edit test-idm-client-ccveu-net
or other application using the libvirt API.
-->

<domstatus state='running' reason='unpaused' pid='17150'>
  <monitor path='/var/lib/libvirt/qemu/domain-59-test-idm-client-ccve/monitor.sock' json='1' type='unix'/>
  <vcpus>
    <vcpu id='0' pid='17156'/>
    <vcpu id='1' pid='17157'/>
  </vcpus>
  <qemuCaps>
    <flag name='kvm'/>
    <flag name='mem-path'/>
    <flag name='ivshmem-doorbell'/>
  </qemuCaps>
  <devices>
    <device alias='balloon0'/>
    <device alias='virtio-disk0'/>
    <device alias='ide0-1-0'/>
  </devices>
  <libDir path='/var/lib/libvirt/qemu/domain-59-test-idm-client-ccve'/>
  <channelTargetDir path='/var/lib/libvirt/qemu/channel/target/domain-59-test-idm-client-ccve'/>
  <domain type='kvm' id='59'>
    <name>test-idm-client-ccveu-net</name>
    <uuid>78177d07-ac0e-4057-b1de-9ccd66cbc3d7</uuid>
    <metadata xmlns:ovirt="http://ovirt.org/vm/tune/1.0">
      <ovirt:qos/>
    </metadata>
    <maxMemory slots='16' unit='KiB'>4294967296</maxMemory>
    <memory unit='KiB'>2097152</memory>
    <currentMemory unit='KiB'>2097152</currentMemory>
    <vcpu placement='static' current='2'>32</vcpu>
    <cputune>
      <shares>1020</shares>
    </cputune>
    <resource>
      <partition>/machine</partition>
    </resource>
    <sysinfo type='smbios'>
      <system>
        <entry name='manufacturer'>Red Hat</entry>
        <entry name='product'>RHEV Hypervisor</entry>
        <entry name='version'>7.3-1.1.el7</entry>
        <entry name='serial'>49c1e6bb-adbb-44ac-8d12-5ba4119cf110</entry>
        <entry name='uuid'>78177d07-ac0e-4057-b1de-9ccd66cbc3d7</entry>
      </system>
    </sysinfo>
    <os>
      <type arch='x86_64' machine='pc-i440fx-rhel7.2.0'>hvm</type>
      <bootmenu enable='yes' timeout='10000'/>
      <smbios mode='sysinfo'/>
    </os>
    <features>
      <acpi/>
    </features>
    <cpu mode='custom' match='exact'>
      <model fallback='allow'>Broadwell</model>
      <topology sockets='16' cores='2' threads='1'/>
      <numa>
        <cell id='0' cpus='0-1' memory='2097152' unit='KiB'/>
      </numa>
    </cpu>
    <clock offset='variable' adjustment='1' basis='utc'>
      <timer name='rtc' tickpolicy='catchup'/>
      <timer name='pit' tickpolicy='delay'/>
      <timer name='hpet' present='no'/>
    </clock>
    <on_poweroff>destroy</on_poweroff>
    <on_reboot>restart</on_reboot>
    <on_crash>destroy</on_crash>
    <devices>
      <emulator>/usr/libexec/qemu-kvm</emulator>
      <disk type='file' device='cdrom'>
        <driver name='qemu' type='raw'/>
        <source startupPolicy='optional'/>
        <backingStore/>
        <target dev='hdc' bus='ide'/>
        <readonly/>
        <alias name='ide0-1-0'/>
        <address type='drive' controller='0' bus='1' target='0' unit='0'/>
      </disk>
      <controller type='usb' index='0' model='piix3-uhci'>
        <alias name='usb'/>
        <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
      </controller>
      <interface type='bridge'>
        <mac address='00:1a:4a:16:03:72'/>
        <source bridge='vlan2593'/>
        <target dev='vnet20'/>
        <model type='virtio'/>
        <filterref filter='vdsm-no-mac-spoofing'/>
        <link state='up'/>
        <boot order='2'/>
        <alias name='net0'/>
        <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
      </interface>
      <channel type='unix'>
        <source mode='bind' path='/var/lib/libvirt/qemu/channels/78177d07-ac0e-4057-b1de-9ccd66cbc3d7.com.redhat.rhevm.vdsm'/>
        <target type='virtio' name='com.redhat.rhevm.vdsm' state='connected'/>
        <alias name='channel0'/>
        <address type='virtio-serial' controller='0' bus='0' port='1'/>
      </channel>
      <input type='mouse' bus='ps2'>
        <alias name='input0'/>
      </input>
    </devices>
    <seclabel type='dynamic' model='dac' relabel='yes'>
      <label>+107:+107</label>
      <imagelabel>+107:+107</imagelabel>
    </seclabel>
  </domain>
</domstatus>
""".strip()

XML_IDM_CLIENT_NO_NAME = """
<!--
WARNING: THIS IS AN AUTO-GENERATED FILE. CHANGES TO IT ARE LIKELY TO BE
OVERWRITTEN AND LOST. Changes to this xml configuration should be made using:
  virsh edit test-idm-client-ccveu-net
or other application using the libvirt API.
-->

<domstatus state='running' reason='unpaused' pid='17150'>
  <monitor path='/var/lib/libvirt/qemu/domain-59-test-idm-client-ccve/monitor.sock' json='1' type='unix'/>
  <vcpus>
    <vcpu id='0' pid='17156'/>
    <vcpu id='1' pid='17157'/>
  </vcpus>
  <libDir path='/var/lib/libvirt/qemu/domain-59-test-idm-client-ccve'/>
  <channelTargetDir path='/var/lib/libvirt/qemu/channel/target/domain-59-test-idm-client-ccve'/>
  <domain type='kvm' id='59'>
    <uuid>78177d07-ac0e-4057-b1de-9ccd66cbc3d7</uuid>
  </domain>
</domstatus>
""".strip()

XML_RHOSP = """
<!--
WARNING: THIS IS AN AUTO-GENERATED FILE. CHANGES TO IT ARE LIKELY TO BE
OVERWRITTEN AND LOST. Changes to this xml configuration should be made using:
  virsh edit instance-000008d6
or other application using the libvirt API.
-->

<domain type='kvm'>
  <name>instance-000008d6</name>
  <uuid>601da52c-450f-4d8e-b502-503431536fa69</uuid>
  <metadata>
    <nova:instance xmlns:nova="http://openstack.org/xmlns/libvirt/nova/1.0">
      <nova:package version="14.0.3-8.el7ost"/>
      <nova:name>django_vm_001</nova:name>
      <nova:creationTime>2017-10-09 08:51:28</nova:creationTime>
      <nova:flavor name="vpc1-cf1-foo-bar">
        <nova:memory>8096</nova:memory>
        <nova:disk>10</nova:disk>
        <nova:swap>0</nova:swap>
        <nova:ephemeral>0</nova:ephemeral>
        <nova:vcpus>4</nova:vcpus>
      </nova:flavor>
      <nova:owner>
        <nova:user uuid="96e9d2b749ea48fcb5a911e6f0e144f2">django_user_01</nova:user>
        <nova:project uuid="5a50e9d0d19746158958be0c759793fb">vpcdi1</nova:project>
      </nova:owner>
      <nova:root type="image" uuid="1a05a423-dfae-428a-ae54-1614d8024e76"/>
    </nova:instance>
  </metadata>
  <memory unit='KiB'>8290304</memory>
  <currentMemory unit='KiB'>8290304</currentMemory>
  <vcpu placement='static'>4</vcpu>
  <cputune>
    <shares>4096</shares>
    <vcpupin vcpu='0' cpuset='1'/>
    <vcpupin vcpu='1' cpuset='2'/>
    <vcpupin vcpu='2' cpuset='13'/>
    <vcpupin vcpu='3' cpuset='14'/>
    <emulatorpin cpuset='1-2,13-14'/>
  </cputune>
  <numatune>
    <memory mode='strict' nodeset='0-1'/>
    <memnode cellid='0' mode='strict' nodeset='0'/>
    <memnode cellid='1' mode='strict' nodeset='1'/>
  </numatune>
  <sysinfo type='smbios'>
    <system>
      <entry name='manufacturer'>Red Hat</entry>
      <entry name='product'>OpenStack Compute</entry>
      <entry name='version'>14.0.3-8.el7ost</entry>
      <entry name='serial'>1b52c42f-b1eb-47f4-a8c0-9904d4735fc9</entry>
      <entry name='uuid'>601da52c-450f-4d8e-b502-50151536fa69</entry>
      <entry name='family'>Virtual Machine</entry>
    </system>
  </sysinfo>
  <os>
    <type arch='x86_64' machine='pc-i440fx-rhel7.3.0'>hvm</type>
    <boot dev='hd'/>
    <smbios mode='sysinfo'/>
  </os>
  <features>
    <acpi/>
    <apic/>
  </features>
  <cpu mode='host-passthrough'>
    <topology sockets='4' cores='1' threads='1'/>
    <numa>
      <cell id='0' cpus='0-1' memory='4145152' unit='KiB'/>
      <cell id='1' cpus='2-3' memory='4145152' unit='KiB'/>
    </numa>
  </cpu>
  <clock offset='utc'>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/var/lib/nova/instances/601da52c-450f-4d8e-b502-50151536fa69/disk'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </disk>
    <disk type='block' device='disk'>
      <driver name='qemu' type='raw' cache='none' io='native'/>
      <source dev='/dev/disk/by-id/dm-uuid-mpath-3600a09803830316d512b4a6b38374143'/>
      <target dev='vdb' bus='virtio'/>
      <serial>dd036ba1-bb5f-4c1a-a369-a918080bff7f</serial>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <interface type='bridge'>
      <mac address='aa:aa:ee:bb:10:aa'/>
      <source bridge='qbrf975e53f-e0'/>
      <target dev='tapf975e53f-e0'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <serial type='file'>
      <source path='/var/lib/nova/instances/601da52c-450f-4d8e-b502-50151536fa69/console.log'/>
      <target port='0'/>
    </serial>
    <serial type='pty'>
      <target port='1'/>
    </serial>
    <console type='file'>
      <source path='/var/lib/nova/instances/601da52c-450f-4d8e-b502-50151536fa69/console.log'/>
      <target type='serial' port='0'/>
    </console>
    <input type='tablet' bus='usb'>
      <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0' keymap='fr'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>
    <video>
      <model type='cirrus' vram='16384' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <stats period='10'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </memballoon>
  </devices>
</domain>
""".strip()

XML_RHOSP_2 = """
<!--
WARNING: THIS IS AN AUTO-GENERATED FILE. CHANGES TO IT ARE LIKELY TO BE
OVERWRITTEN AND LOST. Changes to this xml configuration should be made using:
  virsh edit instance-000008d6
or other application using the libvirt API.
-->

<domain type='kvm'>
  <name>instance-000008d7</name>
  <uuid>601da52c-450f-4d8e-b502-503431536fa69</uuid>
  <metadata>
    <nova:instance xmlns:nova="http://openstack.org/xmlns/libvirt/nova/1.0">
      <nova:package version="14.0.3-8.el7ost"/>
      <nova:name>VM_AT_01</nova:name>
      <nova:creationTime>2017-10-09 08:51:28</nova:creationTime>
    </nova:instance>
  </metadata>
  <memory unit='KiB'>8290304</memory>
  <currentMemory unit='KiB'>8290304</currentMemory>
  <vcpu placement='static'>4</vcpu>
  <cputune>
    <shares>4096</shares>
    <vcpupin vcpu='0' cpuset='1'/>
    <vcpupin vcpu='1' cpuset='2'/>
    <vcpupin vcpu='2' cpuset='13'/>
    <vcpupin vcpu='3' cpuset='14'/>
    <emulatorpin cpuset='1-2,13-14'/>
  </cputune>
  <numatune>
    <memory mode='strict' nodeset='0-1'/>
    <memnode cellid='0' mode='strict' nodeset='0'/>
    <memnode cellid='1' mode='strict' nodeset='1'/>
  </numatune>
  <sysinfo type='smbios'>
    <system>
      <entry name='manufacturer'>Red Hat</entry>
      <entry name='product'>OpenStack Compute</entry>
      <entry name='version'>14.0.3-8.el7ost</entry>
      <entry name='serial'>1b52c42f-b1eb-47f4-a8c0-9904d4735fc9</entry>
      <entry name='uuid'>601da52c-450f-4d8e-b502-50151536fa69</entry>
      <entry name='family'>Virtual Machine</entry>
    </system>
  </sysinfo>
  <os>
    <type arch='x86_64' machine='pc-i440fx-rhel7.3.0'>hvm</type>
    <boot dev='hd'/>
    <smbios mode='sysinfo'/>
  </os>
  <features>
    <acpi/>
    <apic/>
  </features>
  <cpu mode='host-passthrough'>
    <topology sockets='4' cores='1' threads='1'/>
    <numa>
      <cell id='0' cpus='0-1' memory='4145152' unit='KiB'/>
      <cell id='1' cpus='2-3' memory='4145152' unit='KiB'/>
    </numa>
  </cpu>
  <clock offset='utc'>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/var/lib/nova/instances/601da52c-450f-4d8e-b502-50151536fa69/disk'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </disk>
    <disk type='block' device='disk'>
      <driver name='qemu' type='raw' cache='none' io='native'/>
      <source dev='/dev/disk/by-id/dm-uuid-mpath-3600a09803830316d512b4a6b38374143'/>
      <target dev='vdb' bus='virtio'/>
      <serial>dd036ba1-bb5f-4c1a-a369-a918080bff7f</serial>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <interface type='bridge'>
      <mac address='aa:aa:ee:bb:10:aa'/>
      <source bridge='qbrf975e53f-e0'/>
      <target dev='tapf975e53f-e0'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <serial type='file'>
      <source path='/var/lib/nova/instances/601da52c-450f-4d8e-b502-50151536fa69/console.log'/>
      <target port='0'/>
    </serial>
    <serial type='pty'>
      <target port='1'/>
    </serial>
    <console type='file'>
      <source path='/var/lib/nova/instances/601da52c-450f-4d8e-b502-50151536fa69/console.log'/>
      <target type='serial' port='0'/>
    </console>
    <input type='tablet' bus='usb'>
      <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0' keymap='fr'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>
    <video>
      <model type='cirrus' vram='16384' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <stats period='10'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </memballoon>
  </devices>
</domain>
""".strip()


def test_vm_xml():
    xml = qemu_xml.QemuXML(context_wrap(XML_NUMA, path='/etc/libvirt/qemu/vm.xml'))
    assert xml.file_name == 'vm.xml'
    assert xml.vm_name == '05-s00c06h0'
    memnode = xml.get_elements('./numatune/memnode', None)
    assert len(memnode[0].items()) == 3
    assert len(memnode[1].items()) == 3

    # No 'name' found
    xml = qemu_xml.QemuXML(context_wrap(XML_NUMA_NO_NAME, path='/etc/libvirt/qemu/no_name.xml'))
    assert xml.vm_name is None


def test_rhel_7_4():
    xml = qemu_xml.QemuXML(context_wrap(RHEL_7_4_XML, path='/etc/libvirt/qemu/rhel7.4.xml'))
    assert xml.file_name == 'rhel7.4.xml'
    assert xml.vm_name == 'rhel7.4'
    os = xml.get_elements('./os/type')[0]
    assert os.get('arch') == 'x86_64'
    assert os.get('machine') == 'pc-i440fx-2.10'


def test_parse_dom():
    xml = qemu_xml.QemuXML(context_wrap(RHEL_7_4_XML, path='/etc/libvirt/qemu/rhel7.4.xml'))
    dom = xml.parse_dom()
    assert dom.get('vcpu', None) == '4'

    xml = qemu_xml.QemuXML(context_wrap(XML_NUMA_NO_NAME, path='/etc/libvirt/qemu/no_name.xml'))
    dom = xml.parse_dom()
    assert dom.get('vcpu') is None


def test_blank_xml():
    xml = qemu_xml.QemuXML(context_wrap(BLANK_XML, path='/etc/libvirt/qemu/blank.xml'))
    assert xml.file_name == 'blank.xml'
    assert xml.vm_name is None
    assert xml.parse_dom() == {}


def test_rhosp_xml():
    xml = qemu_xml.OpenStackInstanceXML(context_wrap(XML_RHOSP, path='/etc/libvirt/qemu/instance-000008d6.xml'))
    assert xml.domain_name == 'instance-000008d6'
    assert xml.nova.get('version') == '14.0.3-8.el7ost'
    assert xml.nova.get('instance_name') == 'django_vm_001'
    assert xml.nova.get('user') == 'django_user_01'
    assert xml.nova.get('root_disk_type') == 'image'
    assert xml.nova.get('flavor_vcpus') == '4'

    rhosp_xml_2 = qemu_xml.OpenStackInstanceXML(context_wrap(XML_RHOSP_2, path='/etc/libvirt/qemu/instance-000008d7.xml'))
    assert rhosp_xml_2.nova == {'version': '14.0.3-8.el7ost', 'instance_name': 'VM_AT_01', 'created': '2017-10-09 08:51:28'}
    assert rhosp_xml_2.domain_name == 'instance-000008d7'

    # XML not having OSP metadata
    xml = qemu_xml.OpenStackInstanceXML(context_wrap(XML_NUMA, path='/etc/libvirt/qemu/numa_instance_001.xml'))
    assert xml.domain_name == 'numa_instance_001'

    # The XML struture is different from OSP instance XML
    xml = qemu_xml.OpenStackInstanceXML(context_wrap(XML_IDM_CLIENT, path='/etc/libvirt/qemu/idm_001.xml'))
    assert xml.domain_name == 'idm_001'


def test_documentation():
    env = {'xml_numa': qemu_xml.QemuXML(context_wrap(XML_NUMA, path='/etc/libvirt/qemu/vm.xml')),
           'rhosp_xml': qemu_xml.OpenStackInstanceXML(context_wrap(XML_RHOSP, path='/etc/libvirt/qemu/instance-000008d6.xml'))}
    failed_count, tests = doctest.testmod(qemu_xml, globs=env)
    assert failed_count == 0


def test_var_qemu_xml():
    xml = qemu_xml.VarQemuXML(context_wrap(XML_IDM_CLIENT, path='/var/run/libvirt/qemu/test-idm-client-ccveu-net.xml'))
    assert xml.file_name == 'test-idm-client-ccveu-net.xml'
    assert xml.vm_name == 'test-idm-client-ccveu-net'
    assert len(xml.get("qemuCaps")) == 3
    disks = xml.get_elements('./domain/devices/disk')
    assert len(disks) == 1
    assert disks[0].get('device', None) == 'cdrom'

    # No 'name' found
    xml = qemu_xml.VarQemuXML(context_wrap(XML_IDM_CLIENT_NO_NAME, path='/var/run/libvirt/qemu/no_name.xml'))
    assert xml.vm_name is None
