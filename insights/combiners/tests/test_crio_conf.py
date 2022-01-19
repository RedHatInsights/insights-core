from insights.combiners.crio_conf import AllCrioConf
from insights.parsers.crio_conf import CrioConf
from insights.tests import context_wrap


CRIO_CONFIG = """
[crio]
storage_driver = "overlay"
storage_option = [
        "overlay.override_kernel_check=1",
]

[crio.runtime]
selinux = true

[crio.network]
plugin_dirs = [
        "/usr/libexec/cni",
]
[crio.metrics]
""".strip()

CRIO_CONMON_00_CONF = """
[crio]
internal_wipe = true
storage_driver = "device mapper"
""".strip()

CRIO_CONMON_99_CONF = """
[crio]
storage_driver = "overlay2"

[crio.api]
stream_address = ""
stream_port = "10010"

[crio.runtime]
selinux = true
conmon = ""
conmon_cgroup = "pod"
default_env = [
    "NSS_SDB_USE_CACHE=no",
]
log_level = "info"
cgroup_manager = "systemd"
""".strip()


def test_active_crio_conf_nest():
    crio_conf1 = CrioConf(context_wrap(CRIO_CONFIG, path='/etc/crio/crio.conf'))
    crio_conf2 = CrioConf(context_wrap(CRIO_CONMON_00_CONF, path='/etc/crio/crio.conf.d/00-conmon.conf'))
    crio_conf3 = CrioConf(context_wrap(CRIO_CONMON_99_CONF, path='/etc/crio/crio.conf.d/99-conmon.conf'))
    result = AllCrioConf([crio_conf1, crio_conf2, crio_conf3])
    assert result.has_option("crio", "internal_wipe")
    assert result.has_option("crio.runtime", "default_env")
    assert result.get("crio.api", "stream_port") == "\"10010\""
    assert result.get('crio', 'storage_driver') == "\"overlay2\""
    assert "crio.network" in result.sections()
    assert "realmstest" not in result.sections()
    assert result.has_section("crio.metrics")
    assert not result.has_option("crio.metrics", "nosuchoption")
    assert not result.options("realmsno")
    assert result.files == ['/etc/crio/crio.conf', '/etc/crio/crio.conf.d/00-conmon.conf',
                            '/etc/crio/crio.conf.d/99-conmon.conf']
