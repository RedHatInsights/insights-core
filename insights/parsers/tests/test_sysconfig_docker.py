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

from insights.parsers.sysconfig import DockerSysconfig
from insights.tests import context_wrap

DOCKER_SYSCONFIG_STD = """
# /etc/sysconfig/docker

# Modify these options if you want to change the way the docker daemon runs
OPTIONS='--selinux-enabled'

DOCKER_CERT_PATH=/etc/docker

# If you want to add your own registry to be used for docker search and docker
# pull use the ADD_REGISTRY option to list a set of registries, each prepended
# with --add-registry flag. The first registry added will be the first registry
# searched.
ADD_REGISTRY='--add-registry registry.access.redhat.com'

# If you want to block registries from being used, uncomment the BLOCK_REGISTRY
# option and give it a set of registries, each prepended with --block-registry
# flag. For example adding docker.io will stop users from downloading images
# from docker.io
# BLOCK_REGISTRY='--block-registry'

# If you have a registry secured with https but do not have proper certs
# distributed, you can tell docker to not look for full authorization by
# adding the registry to the INSECURE_REGISTRY line and uncommenting it.
# INSECURE_REGISTRY='--insecure-registry'

# On an SELinux system, if you remove the --selinux-enabled option, you
# also need to turn on the docker_transition_unconfined boolean.
# setsebool -P docker_transition_unconfined 1

# Location used for temporary files, such as those created by
# docker load and build operations. Default is /var/lib/docker/tmp
# Can be overriden by setting the following environment variable.
# DOCKER_TMPDIR=/var/tmp

# Controls the /etc/cron.daily/docker-logrotate cron job status.
# To disable, uncomment the line below.
# LOGROTATE=false
"""


def test_standard_content():
    context = context_wrap(DOCKER_SYSCONFIG_STD, 'etc/sysconfig/docker')
    sysconf = DockerSysconfig(context)

    assert sorted(sysconf.keys()) == sorted(['OPTIONS', 'DOCKER_CERT_PATH', 'ADD_REGISTRY'])
    assert 'OPTIONS' in sysconf
    assert sysconf['OPTIONS'] == '--selinux-enabled'
    assert sysconf.options == '--selinux-enabled'
    assert 'DOCKER_CERT_PATH' in sysconf
    assert sysconf['DOCKER_CERT_PATH'] == '/etc/docker'
    assert 'ADD_REGISTRY' in sysconf
    assert sysconf['ADD_REGISTRY'] == '--add-registry registry.access.redhat.com'
    assert sysconf.unparsed_lines == []
