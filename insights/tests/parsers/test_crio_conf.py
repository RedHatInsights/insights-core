import doctest

from insights.parsers import crio_conf
from insights.parsers.crio_conf import CrioConf
from insights.tests import context_wrap

CRIO_CONF_DATA = """
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

[crio.runtime.workloads]
""".strip()

CONF_PATH = '/etc/crio/crio.conf'


def test_crio_conf():
    confs = CrioConf(context_wrap(CRIO_CONF_DATA, path=CONF_PATH))
    assert 'crio' in confs.sections()
    assert 'crio.runtime.workloads' in confs.sections()
    assert confs.file_name == 'crio.conf'
    assert confs.has_option('crio', 'storage_option')
    assert confs.has_option('crio.runtime', 'hooks_dir')
    assert confs.has_option('crio.metrics', 'metrics_opt')
    assert confs.has_option('crio.metrics', 'metrics_collectors')
    assert confs.has_option('crio.runtime', 'default_sysctls')
    assert confs.has_option('crio.runtime', 'test_sysctls')
    assert confs.has_option('crio.runtime', 'default_env')
    assert "NSS_SDB_USE_CACHE=no" in confs.get('crio.runtime', 'default_env')
    assert confs.has_option('crio.network', 'plugin_dirs')
    assert "/var/lib/cni/bin" in confs.get('crio.network', 'plugin_dirs')
    assert "/usr/libexec/cni" in confs.get('crio.network', 'plugin_dirs')
    assert confs.get('crio.metrics', 'metrics_port') == '9537'


def test_crio_conf_documentation():
    failed_count, tests = doctest.testmod(
        crio_conf,
        globs={'crio_conf': CrioConf(context_wrap(CRIO_CONF_DATA))}
    )
    assert failed_count == 0
