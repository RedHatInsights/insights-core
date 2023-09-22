"""
VMwareToolsConf - file ``/etc/vmware-tools/tools.conf``
=======================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.vmware_tools_conf)
class VMwareToolsConf(IniConfigFile):
    """
    The VMware tools configuration file ``/etc/vmware-tools/tools.conf``
    is in the standard 'ini' format and is read by the IniConfigFile
    parser. ``vmtoolsd.service`` provided by ``open-vm-tools`` package is
    configured using ``/etc/vmware-tools/tools.conf``.

    Sample ``/etc/vmware-tools/tools.conf`` file::

        [guestinfo]
        disable-query-diskinfo = true

        [logging]
        log = true
        vmtoolsd.level = debug
        vmtoolsd.handler = file
        vmtoolsd.data = /tmp/vmtoolsd.log

    Examples:
        >>> type(conf)
        <class 'insights.parsers.vmware_tools_conf.VMwareToolsConf'>
        >>> list(conf.sections()) == [u'guestinfo', u'logging']
        True
        >>> conf.has_option('guestinfo', 'disable-query-diskinfo')
        True
        >>> conf.getboolean('guestinfo', 'disable-query-diskinfo')
        True
        >>> conf.get('logging', 'vmtoolsd.data')
        '/tmp/vmtoolsd.log'
    """
    pass
