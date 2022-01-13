import doctest

from insights.parsers import crio_confd_conmon
from insights.parsers.crio_confd_conmon import CrioConfdConmon
from insights.tests import context_wrap

CRIO_CONFD_CONMON = """
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

[crio.apps]
default_runtime = "podman"
""".strip()

CONF_PATH = '/etc/crio/crio.conf.d/99-conmon.conf'


def test_crio_confd_conmon():
    confs = CrioConfdConmon(context_wrap(CRIO_CONFD_CONMON, path=CONF_PATH))
    assert confs.file_name == '99-conmon.conf'
    assert confs.get('crio.runtime', 'default_runtime') == "\"runc\""


def test_crio_confd_conmon_documentation():
    failed_count, tests = doctest.testmod(
        crio_confd_conmon,
        globs={'crio_confd': CrioConfdConmon(context_wrap(CRIO_CONFD_CONMON))}
    )
    assert failed_count == 0
