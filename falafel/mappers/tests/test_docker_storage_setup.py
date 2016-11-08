from falafel.mappers.docker_storage_setup import DockerStorageSetup
from falafel.tests import context_wrap

DOCKER_STORAGE_SETUP1 = """
# Edit this file to override any configuration options specified in
# /usr/lib/docker-storage-setup/docker-storage-setup.
#
# For more details refer to "man docker-storage-setup"
VG=vgtest
AUTO_EXTEND_POOL=yes
##name = mydomain
POOL_AUTOEXTEND_THRESHOLD=60
POOL_AUTOEXTEND_PERCENT=20
""".strip()

DOCKER_STORAGE_SETUP2 = """
#comment
# comment
# comment = comment
# comment = comment = comment
#comment=comment
#comment=comment=comment
option_a=value_a
option_b = value_b
option_c= value_c
option_d =value_d
broken_option_e = value_e = value_2_e
broken_option_f=value_f=value_2_f
broken_option_g
option_h = value_h # some comment
option_i = value_i # this must be accessible, even after all these errors
""".strip()

DOCKER_STORAGE_SETUP_PATH = "etc/sysconfig/docker-storage-setup"


def test_constructor():
    context = context_wrap(DOCKER_STORAGE_SETUP1, DOCKER_STORAGE_SETUP_PATH)
    result = DockerStorageSetup(context)

    assert 'POOL_AUTOEXTEND_THRESHOLD=60' in result.active_lines_unparsed
    assert "20" == result.active_settings["POOL_AUTOEXTEND_PERCENT"]
    assert "name" not in result.active_settings
    assert "##name" not in result.active_settings
    assert "vgtest" == result["VG"]

    context = context_wrap(DOCKER_STORAGE_SETUP2, DOCKER_STORAGE_SETUP_PATH)
    result = DockerStorageSetup(context)

    assert "comment" not in result.active_settings
    assert "broken_option_g" not in result.active_settings
    assert "value_i" == result["option_i"]


def test_active_lines_unparsed():
    context = context_wrap(DOCKER_STORAGE_SETUP1, DOCKER_STORAGE_SETUP_PATH)
    result = DockerStorageSetup(context)
    test_active_lines = []
    for line in DOCKER_STORAGE_SETUP1.split("\n"):
        if not line.strip().startswith("#"):
            if line.strip():
                test_active_lines.append(line)
    assert test_active_lines == result.active_lines_unparsed


def build_active_settings_expected():
    active_settings = {}
    for line in DOCKER_STORAGE_SETUP1.split("\n"):
        if not line.strip().startswith("#"):
            if line.strip():
                try:
                    key, value = line.split("=", 1)
                    key, value = key.strip(), value.strip()
                except:
                    pass
                else:
                    active_settings[key] = value
    return active_settings


def test_active_settings():
    context = context_wrap(DOCKER_STORAGE_SETUP1, DOCKER_STORAGE_SETUP_PATH)
    result = DockerStorageSetup(context)
    active_settings = build_active_settings_expected()
    assert active_settings == result.active_settings
