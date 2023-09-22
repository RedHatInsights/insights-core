"""
AutoFSConf - file ``/etc/autofs.conf``
======================================
"""

from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.autofs_conf)
class AutoFSConf(IniConfigFile):
    """
    The `/etc/autofs.conf` file is in a standard '.ini' format, and this parser
    uses the IniConfigFile base class to read this.

    Sample configuration::

        [ autofs ]
        timeout = 300
        browse_mode = no
        mount_nfs_default_protocol = 4

        [ amd ]
        dismount_interval = 300

    Examples:
        >>> type(config)
        <class 'insights.parsers.autofs_conf.AutoFSConf'>
        >>> config.sections()
        ['autofs', 'amd']
        >>> config.has_option('amd', 'dismount_interval')
        True
        >>> config.get('amd', 'dismount_interval')
        '300'
        >>> config.getint('autofs', 'timeout')
        300
        >>> config.getboolean('autofs', 'browse_mode')
        False
    """
    pass
