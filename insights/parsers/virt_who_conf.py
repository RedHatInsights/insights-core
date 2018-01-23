"""
VirtWhoConf - File ``/etc/virt-who.conf`` and ``/etc/virt-who.d/*.conf``
========================================================================

The ``VirtWhoConf`` class parses the virt-who configuration files in `ini-like`
format.

    .. note::

        The configuration files under ``/etc/virt-who.d/`` might contain
        sensitive information, like ``password``. It must be filtered.
"""

from .. import parser, LegacyItemAccess, IniConfigFile, add_filter
from insights.specs import Specs

filter_list = [
        '[',
        'interval',
        'oneshot',
        'type',
        'server',
        'debug',
        'log_',
        'configs',
        'owner',
        'env',
]
add_filter(Specs.virt_who_conf, filter_list)


@parser(Specs.virt_who_conf)
class VirtWhoConf(LegacyItemAccess, IniConfigFile):
    """
    Parse the ``virt-who`` configuration files ``/etc/virt-who.conf`` and
    ``/etc/virt-who.d/*.conf``.

    Sample configuration file::

        ## This is a template for virt-who global configuration files. Please see
        ## virt-who-config(5) manual page for detailed information.
        ##
        ## virt-who checks /etc/virt-who.conf for sections 'global' and 'defaults'.
        ## The sections and their values are explained below.
        ## NOTE: These sections retain their special meaning and function only when present in /etc/virt-who.conf
        ##
        ## You can uncomment and fill following template or create new file with
        ## similar content.

        #Terse version of the general config template:
        [global]

        interval=3600
        #reporter_id=
        debug=False
        oneshot=False
        #log_per_config=False
        #log_dir=
        #log_file=
        #configs=

        [defaults]
        owner=Satellite
        env=Satellite

    Examples:

        >>> vwho_conf = shared[VirtWhoConf]
        >>> 'global' in vwho_conf
        True
        >>> vwho_conf.has_option('global', 'debug')
        True
        >>> vwho_conf.get('global', 'oneshot')
        "False"
        >>> vwho_conf.getboolean('global', 'oneshot')
        False
        >>> vwho_conf.get('global', 'interval')
        "3600"
        >>> vwho_conf.getint('global', 'interval')
        3600
        >>> vwho_conf.items('defaults')
        {'owner': 'Satellite', 'env': 'Satellite'}
    """
    pass
