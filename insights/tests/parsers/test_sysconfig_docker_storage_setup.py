from insights.parsers.sysconfig import DockerStorageSetupSysconfig
from insights.tests import context_wrap

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


def test_docker_storage_setup():
    context = context_wrap(DOCKER_STORAGE_SETUP1)
    result = DockerStorageSetupSysconfig(context)

    assert 'POOL_AUTOEXTEND_THRESHOLD' in result
    assert "20" == result["POOL_AUTOEXTEND_PERCENT"]
    assert "name" not in result
    assert "##name" not in result
    assert "vgtest" == result["VG"]

    context = context_wrap(DOCKER_STORAGE_SETUP2)
    result = DockerStorageSetupSysconfig(context)

    assert "comment" not in result
    assert "broken_option_g" not in result
    # Options with spaces around the '=' are not allowed in /etc/sysconfig
    assert "option_i" not in result
