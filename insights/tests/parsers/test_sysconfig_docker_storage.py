from insights.parsers.sysconfig import DockerSysconfigStorage
from insights.tests import context_wrap


DOCKER_CONFIG_STORAGE = """
DOCKER_STORAGE_OPTIONS="--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/dockervg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true"
""".strip()


def test_sysconfig_docker_content():
    context = context_wrap(DOCKER_CONFIG_STORAGE, 'etc/sysconfig/docker-storage')
    sysconf = DockerSysconfigStorage(context)

    assert sorted(sysconf.keys()) == sorted(['DOCKER_STORAGE_OPTIONS'])
    assert 'DOCKER_STORAGE_OPTIONS' in sysconf
    assert sysconf['DOCKER_STORAGE_OPTIONS'] == "--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/dockervg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true"
    assert sysconf.storage_options == "--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/dockervg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true"
