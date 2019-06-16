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

from insights.parsers.sysconfig import MemcachedSysconfig
from insights.tests import context_wrap

MEMCACHED_CONFIG = """
PORT="11211"
USER="memcached"
# max connection 2048
MAXCONN="2048"
# set ram size to 2048 - 2GiB
CACHESIZE="4096"
# disable UDP and listen to loopback ip 127.0.0.1, for network connection use real ip e.g., 10.0.0.5
OPTIONS="-U 0 -l 127.0.0.1"
""".strip()


def test_sysconfig_memcached():
    context = context_wrap(MEMCACHED_CONFIG, 'etc/sysconfig/memcached')
    conf = MemcachedSysconfig(context)

    assert 'OPTIONS' in conf
    assert 'FOO' not in conf
    assert conf.get('OPTIONS') == '-U 0 -l 127.0.0.1'
    assert conf.get('USER') == 'memcached'
