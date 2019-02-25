"""
QemuXML file ``/etc/libvirt/qemu/*.xml`` and ``/var/run/libvirt/qemu/*.xml``
----------------------------------------------------------------------------

Parsers provided by this module are:

QemuXML - file ``/etc/libvirt/qemu/*.xml``
------------------------------------------

VarQemuXML - file ``/var/run/libvirt/qemu/*.xml``
-------------------------------------------------
"""
from .. import XMLParser, parser
from insights.specs import Specs


@parser(Specs.qemu_xml)
class QemuXML(XMLParser):
    """This class parses xml files under ``/etc/libvirt/qemu/`` using
    ``XMLParser`` base parser.

    Sample file::

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
              <mac address='b2:59:73:15:00:00'/>
              <source>
                <address type='pci' domain='0x0000' bus='0x04' slot='0x10' function='0x0'/>
              </source>
              <rom bar='on' file='/opt/vcp/share/ipxe/808610ed.rom'/>
              <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
            </interface>
            <interface type='hostdev' managed='yes'>
              <mac address='b2:59:73:15:00:01'/>
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

    Examples:
        >>> xml_numa.file_name == 'vm.xml'
        True
        >>> xml_numa.vm_name == '05-s00c06h0'
        True
        >>> memnode = xml_numa.get_elements('./numatune/memnode', None)
        >>> len(memnode[0].items()) == 3
        True
        >>> len(memnode[1].items()) == 3
        True
        >>> memnode[0].get('cellid') == '0'
        True
        >>> memnode[1].get('mode') == 'strict'
        True
    """
    def parse_dom(self):
        if self.dom is None:
            return
        else:
            domain = {}
            for child in self.dom:
                if len(child) == 0:
                    domain[child.tag] = child.text
                else:
                    domain[child.tag] = [c.items() for c in child]

            return domain

    @property
    def vm_name(self):
        return self.data.get('name', None)


@parser(Specs.var_qemu_xml)
class VarQemuXML(QemuXML):
    """This class parses xml files under ``/var/run/libvirt/qemu/`` using
    ``QemuXML`` base parser.

    Sample file::

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
    """
    @property
    def vm_name(self):
        if self.get_elements("./domain/name"):
            return self.get_elements("./domain/name")[0].text
