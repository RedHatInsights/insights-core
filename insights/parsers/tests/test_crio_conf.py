import doctest

from insights.parsers import crio_conf
from insights.parsers.crio_conf import CrioConf
from insights.tests import context_wrap

CRIO_CONF_DATA = """
[crio]
storage_option=[ "overlay.imagestore=/mnt/overlay", ]

[crio.runtime]
selinux = true

[crio.network]
plugin_dirs = [
    "/usr/libexec/cni",
]

[crio.metrics]
enable_metrics = true
metrics_port = 9537
""".strip()

CONF_PATH = '/etc/crio/crio.conf'


def test_crio_conf():
    confs = CrioConf(context_wrap(CRIO_CONF_DATA, path=CONF_PATH))
    assert 'crio' in confs.sections()
    assert confs.file_name == 'crio.conf'
    assert confs.has_option('crio', 'storage_option')
    assert confs.get('crio.metrics', 'metrics_port') == '9537'


def test_crio_conf_documentation():
    failed_count, tests = doctest.testmod(
        crio_conf,
        globs={'crio_conf': CrioConf(context_wrap(CRIO_CONF_DATA))}
    )
    assert failed_count == 0
