"""
VirtWhoConf - File ``/etc/virt-who.conf`` and ``/etc/virt-who.d/*.conf``
========================================================================

The ``VirtWhoConf`` class parses the virt-who configuration files in `ini-like`
format.

    .. note::

        The configuration files under ``/etc/virt-who.d/`` might contain
        sensitive information, like ``password``. It must be filtered.
"""

from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
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
class VirtWhoConf(IniConfigFile):
    """
    Parse the ``virt-who`` configuration files ``/etc/virt-who.conf`` and
    ``/etc/virt-who.d/*.conf``.

    Sample configuration file::

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
        >>> type(conf)
        <class 'insights.parsers.virt_who_conf.VirtWhoConf'>
        >>> 'global' in conf
        True
        >>> conf.has_option('global', 'debug')
        True
        >>> conf.get('global', 'oneshot')
        'False'
        >>> conf.getboolean('global', 'oneshot')
        False
        >>> conf.get('global', 'interval')
        '3600'
        >>> conf.getint('global', 'interval')
        3600
    """
    pass
