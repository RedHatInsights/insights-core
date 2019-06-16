#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
