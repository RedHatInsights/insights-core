"""
SosConf - file ``/etc/sos.conf`` or ``/etc/sos/sos.conf``
=========================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.sos_conf)
class SosConf(IniConfigFile):
    """
    This class provides parsing for the file ``/etc/sos.conf``.
    On RHEL 8 and later, the file location is ``/etc/sos/sos.conf``.

    Sample input data is in the format::

        [general]
        #verbose = 3
        #verify = yes
        batch = yes
        #log-size = 15

        [plugins]
        disable = rpm, selinux, dovecot

        [tunables]
        #rpm.rpmva = off

    Examples:
        >>> type(sos_conf)
        <class 'insights.parsers.sos_conf.SosConf'>
        >>> 'plugins' in sos_conf.sections()
        True
        >>> sos_conf.get("plugins", "disable")
        'rpm, selinux, dovecot'
        >>> sos_conf.getboolean("general", "batch")
        True
    """
    pass
