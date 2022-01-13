"""
CrioConf - file ``/etc/crio/crio.conf``
=======================================
"""

from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.crio_conf)
class CrioConf(IniConfigFile):
    """
    The ``CrioConf`` class parses the information in the file
    ``/etc/crio/crio.conf``. See the ``IniConfigFile`` class for more
    information on attributes and methods.

    Sample input data looks like::

        [crio]

        [crio.runtime]
        selinux = true

        [crio.network]
        plugin_dirs = [
            "/usr/libexec/cni",
        ]

        [crio.metrics]
        enable_metrics = true
        metrics_port = 9537

    Examples:
        >>> "crio" in crio_conf
        True
        >>> crio_conf.has_option('crio.runtime', 'selinux')
        True
        >>> crio_conf.get('crio.metrics', 'metrics_port')
        '9537'
    """
    pass
