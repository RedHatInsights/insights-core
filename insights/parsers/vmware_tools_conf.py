"""
VMwareToolsConf - file ``/etc/vmware-tools/tools.conf``
=======================================================

The VMware tools configuration file ``/etc/vmware-tools/tools.conf``
is in the standard 'ini' format and is read by the IniConfigFile
parser. ``vmtoolsd.service`` provided by ``open-vm-tools`` package is
configured using ``/etc/vmware-tools/tools.conf``.

Examples:

    >>> from insights.parsers.vmware_tools_conf import VMwareToolsConf
    >>> from insights.tests import context_wrap
    >>> CONF = '''
    ... [guestinfo]
    ... disable-query-diskinfo = true
    ...
    ... [logging]
    ... log = true
    ...
    ... vmtoolsd.level = debug
    ... vmtoolsd.handler = file
    ... vmtoolsd.data = /tmp/vmtoolsd.log
    ... '''
    >>> result = VMwareToolsConf(context_wrap(CONF))
    >>> result.sections()
    ['guestinfo', 'logging']
    >>> result.has_option('guestinfo', 'disable-query-diskinfo')
    True
    >>> result.getboolean('guestinfo', 'disable-query-diskinfo')
    True
    >>> result.get('guestinfo', 'disable-query-diskinfo')
    'true'

"""

from .. import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.vmware_tools_conf)
class VMwareToolsConf(IniConfigFile):
    """Class for VMware tool configuration file content."""
    pass
