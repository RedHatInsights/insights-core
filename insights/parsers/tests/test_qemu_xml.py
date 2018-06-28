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
    assert xml.parse_dom() is None


def test_documentation():
    env = {'xml_numa': qemu_xml.QemuXML(context_wrap(XML_NUMA, path='/etc/libvirt/qemu/vm.xml'))}
    failed_count, tests = doctest.testmod(qemu_xml, globs=env)
    assert failed_count == 0
