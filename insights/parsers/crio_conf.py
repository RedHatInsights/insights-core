"""
CrioConf - files ``/etc/crio/crio.conf`` and ``/etc/crio/crio.conf.d/*``
========================================================================
"""

from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.crio_conf)
class CrioConf(IniConfigFile):
    """
    The ``CrioConf`` class parses the information in the files
    ``/etc/crio/crio.conf`` and ``/etc/crio/crio.conf.d/*``.
    See the ``IniConfigFile`` class for more information on attributes and methods.

    Sample input data looks like::

        [crio]
        storage_option=[ "overlay.imagestore=/mnt/overlay", "overlay.size=1G", ]

        [crio.runtime]
        hooks_dir = [ "/etc/containers/oci/hooks.d", ]
        selinux = true
        default_sysctls = [
        ]

        test_sysctls = [
        \t
        ]

        default_env = [
            "NSS_SDB_USE_CACHE=no",
        ]

        [crio.network]
        plugin_dirs = [
            "/var/lib/cni/bin",
            "/usr/libexec/cni",
        ]

        [crio.metrics]
        metrics_opt = [ "operations" ]
        enable_metrics = true
        metrics_port = 9537
        metrics_collectors = [
          "operations",
          "operations_latency_microseconds_total",
          "operations_latency_microseconds",
          "operations_errors"
          "containers_oom_total",
          "containers_oom",
          # Drop metrics with excessive label cardinality.
          # "image_pulls_by_digest",
          "image_pulls_layer_size",
          # "image_pulls_by_name",
          # "image_pulls_by_name_skipped",
          # "image_pulls_failures",
          # "image_pulls_successes",
          # "image_layer_reuse",
        ]

    Examples:
        >>> "crio" in crio_conf
        True
        >>> crio_conf.has_option('crio.runtime', 'selinux')
        True
        >>> crio_conf.get('crio.metrics', 'metrics_port')
        '9537'
    """
    pass
