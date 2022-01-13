"""
CrioConfdConmon - file ``/etc/crio/crio.conf.d/*-conmon.conf``
==============================================================
"""

from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.crio_confd_conmon)
class CrioConfdConmon(IniConfigFile):
    """
    The ``CrioConfdConmon`` class parses the information in the files
    ``/etc/crio/crio.conf.d/*-conmon.conf``. See the ``IniConfigFile`` class for more
    information on attributes and methods.

    Sample input data looks like::

        [crio.runtime]
        default_runtime = "runc"
        no_pivot = false
        decryption_keys_path = "/etc/crio/keys/"
        conmon = ""
        conmon_cgroup = "system.slice"
        conmon_env = [
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        ]
        default_env = [
        ]
        selinux = true
        seccomp_profile = ""
        apparmor_profile = "crio-default"
        cgroup_manager = "systemd"
        default_capabilities = [
            "CHOWN",
            "SETUID",
            "SETPCAP",
            "NET_BIND_SERVICE",
            "KILL",
        ]

    Examples:
        >>> "crio.runtime" in crio_confd
        True
        >>> crio_confd.has_option('crio.runtime', 'conmon')
        True
        >>> crio_confd.get('crio.runtime', 'decryption_keys_path')
        '"/etc/crio/keys/"'
    """
    pass
