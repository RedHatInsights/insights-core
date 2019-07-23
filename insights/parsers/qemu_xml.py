"""
QemuXML - file ``/etc/libvirt/qemu/*.xml`` and ``/var/run/libvirt/qemu/*.xml``
==============================================================================

Parsers provided by this module are:

QemuXML - file ``/etc/libvirt/qemu/*.xml``
------------------------------------------

VarQemuXML - file ``/var/run/libvirt/qemu/*.xml``
-------------------------------------------------

OpenStackInstanceXML - file ``/etc/libvirt/qemu/*.xml``
-------------------------------------------------------
"""
from insights.components.openstack import IsOpenStackCompute
from insights.specs import Specs
from .. import XMLParser, parser


class BaseQemuXML(XMLParser):
    """Base class for parsing Qemu XML files. It uses ``XMLParser`` mixin
    class.

    Attributes:
        vm_name(str): Name of VM

    """
    def parse_content(self, content):
        super(BaseQemuXML, self).parse_content(content)

        # Setting vm_name attribute
        if self.dom and self.get_elements('./domain/name'):
            self.vm_name = self.get_elements('./domain/name')[0].text
        else:
            self.vm_name = self.data.get('name', None)

    def parse_dom(self):
        """Parse xml information in :attr:`data` and return.

        Returns:
            dict: Parsed xml data. An empty dictionary when content is blank.
        """
        if self.dom is None:
            return {}

        domain = {}
        for child in self.dom:
            if len(child) == 0:
                domain[child.tag] = child.text
            else:
                domain[child.tag] = [c.items() for c in child]
        return domain


@parser(Specs.qemu_xml)
class QemuXML(BaseQemuXML):
    """This class parses xml files under ``/etc/libvirt/qemu/`` using
    ``BaseQemuXML`` base parser.

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
    pass


@parser(Specs.var_qemu_xml)
class VarQemuXML(BaseQemuXML):
    """This class parses xml files under ``/var/run/libvirt/qemu/`` using
    ``BaseQemuXML`` base parser.

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
          </vcpus>
          <qemuCaps>
            <flag name='kvm'/>
            <flag name='mem-path'/>
          </qemuCaps>
          <devices>
            <device alias='balloon0'/>
          </devices>
          <libDir path='/var/lib/libvirt/qemu/domain-59-test-idm-client-ccve'/>
          <domain type='kvm' id='59'>
            <name>test-idm-client-ccveu-net</name>
            <uuid>78177d07-ac0e-4057-b1de-9ccd66cbc3d7</uuid>
            <metadata xmlns:ovirt="http://ovirt.org/vm/tune/1.0">
              <ovirt:qos/>
            </metadata>
            <maxMemory slots='16' unit='KiB'>4294967296</maxMemory>
            <memory unit='KiB'>2097152</memory>
            <os>
              <type arch='x86_64' machine='pc-i440fx-rhel7.2.0'>hvm</type>
              <bootmenu enable='yes' timeout='10000'/>
              <smbios mode='sysinfo'/>
            </os>
            <devices>
              <emulator>/usr/libexec/qemu-kvm</emulator>
              <disk type='file' device='cdrom'>
                <driver name='qemu' type='raw'/>
                <source startupPolicy='optional'/>
              </disk>
            </devices>
          </domain>
        </domstatus>
    """
    pass


@parser(Specs.qemu_xml, IsOpenStackCompute)
class OpenStackInstanceXML(BaseQemuXML):
    """Parse OpenStack instances metadata based on the class ``BaseQemuXML``.

    This parser depends on ``insights.components.openstack.IsOpenStackCompute``
    and will be fired only if the dependency is met.

    Sample metadata section in the XML file::

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

    Examples:
        >>> rhosp_xml.domain_name
        'instance-000008d6'
        >>> rhosp_xml.nova.get('version')
        '14.0.3-8.el7ost'
        >>> rhosp_xml.nova.get('instance_name')
        'django_vm_001'
        >>> rhosp_xml.nova.get('user')
        'django_user_01'
        >>> rhosp_xml.nova.get('root_disk_type')
        'image'
        >>> rhosp_xml.nova.get('flavor_vcpus')
        '4'

    Attributes:
        domain_name(str): XML domain name.
        nova(dict): OpenStack Compute Metadata.
    """
    def parse_content(self, content):
        super(OpenStackInstanceXML, self).parse_content(content)
        self.domain_name = self.file_name.strip('.xml')

        # Parse OpenStack Compute(Nova) metadata
        ns = {'nova': 'http://openstack.org/xmlns/libvirt/nova/1.0'}
        self.nova = {}
        if self.dom and self.get_elements('./metadata'):
            for i in self.get_elements('./metadata')[0]:
                self.nova['version'] = i.findall('nova:package', ns)[0].get('version')

                # Instance meta
                self.nova['instance_name'] = i.findall('nova:name', ns)[0].text
                self.nova['created'] = i.findall('nova:creationTime', ns)[0].text

                # Flavor meta
                if i.findall('nova:flavor', ns):
                    flavor = i.findall('nova:flavor', ns)[0]
                    self.nova['flavor_name'] = flavor.get('name')
                    self.nova['flavor_memory'] = flavor.findall('nova:memory', ns)[0].text
                    self.nova['flavor_disk'] = flavor.findall('nova:disk', ns)[0].text
                    self.nova['flavor_swap'] = flavor.findall('nova:swap', ns)[0].text
                    self.nova['flavor_ephemeral'] = flavor.findall('nova:ephemeral', ns)[0].text
                    self.nova['flavor_vcpus'] = flavor.findall('nova:vcpus', ns)[0].text

                # Owner meta
                if i.findall('nova:owner', ns):
                    owner = i.findall('nova:owner', ns)[0]
                    user = owner.findall('nova:user', ns)[0]
                    project = owner.findall('nova:project', ns)[0]
                    self.nova['user'] = user.text
                    self.nova['user_uuid'] = user.get('uuid')
                    self.nova['project'] = project.text
                    self.nova['project_uuid'] = project.get('uuid')

                # root disk meta
                if i.findall('nova:root', ns):
                    root = i.findall('nova:root', ns)[0]
                    self.nova['root_disk_type'] = root.get('type')
                    self.nova['root_disk_uuid'] = root.get('uuid')
