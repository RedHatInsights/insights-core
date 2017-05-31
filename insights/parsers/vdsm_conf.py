"""
VDSMConfIni - file ``/etc/vdsm/vdsm.conf``
==========================================

The VDSM configuration file ``/etc/vdsm/vdsm.conf`` is in the standard 'ini'
format and is read by the IniConfigFile parser.

Sample configuration file::

    [vars]
    ssl = true
    cpu_affinity = 1

    [addresses]
    management_port = 54321
    qq = 345


Examples:
    >>> vdsm_conf = shared[VDSMConfIni]
    >>> 'vars' in vdsm_conf
    True
    >>> vdsm_conf.get('addresses', 'qq')
    '345'
    >>> vdsm_conf.getboolean('vars', 'ssl')
    True
    >>> vdsm_conf.getint('addresses', 'management_port')
    54321
"""

from .. import IniConfigFile, parser


@parser("vdsm.conf")
class VDSMConfIni(IniConfigFile):
    """Class for VDSM configuration file content."""
    pass
