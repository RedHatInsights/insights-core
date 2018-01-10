"""
AutoFSConf - file ``/etc/autofs.conf``
======================================

The `/etc/autofs.conf` file is in a standard '.ini' format, and this parser
uses the IniConfigFile base class to read this.

Example:
    >>> config = shared[AutoFSConf]
    >>> config.sections()
    ['autofs', 'amd']
    >>> config.items('autofs')
    ['timeout', 'browse_mode', 'mount_nfs_default_protocol']
    >>> config.has_option('amd', 'map_type')
    True
    >>> config.get('amd', 'map_type')
    'file'
    >>> config.getint('autofs', 'timeout')
    300
    >>> config.getboolean('autofs', 'browse_mode')
    False
"""

from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.autofs_conf)
class AutoFSConf(IniConfigFile):
    """
        /etc/autofs.conf is a standard INI style config file.
    """
    pass
