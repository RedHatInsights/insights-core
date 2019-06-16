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

import doctest
import pytest
from insights.configtree import first, last
from insights.parsers import corosync, SkipException
from insights.tests import context_wrap

corosync_content = """
# Corosync init script configuration file

# COROSYNC_INIT_TIMEOUT specifies number of seconds to wait for corosync
# initialization (default is one minute).
COROSYNC_INIT_TIMEOUT=60

# COROSYNC_OPTIONS specifies options passed to corosync command
# (default is no options).
# See "man corosync" for detailed descriptions of the options.
COROSYNC_OPTIONS=""
"""

COROSYNC_CONF = """
totem {
    version: 2
    secauth: off
    cluster_name: tripleo_cluster
    transport: udpu
    token: 10000
}

nodelist {
    node {
        ring0_addr: overcloud-controller-0
        nodeid: 1
    }

    node {
        ring0_addr: overcloud-controller-1
        nodeid: 2
    }

    node {
        ring0_addr: overcloud-controller-2
        nodeid: 3
    }
}

quorum {
    provider: corosync_votequorum
}

logging {
    to_logfile: yes
    logfile: /var/log/cluster/corosync.log
    to_syslog: yes
}
""".strip()

COROSYNC_CONF_2 = """
totem {
    version: 2
    secauth: off
    cluster_name: tripleo_cluster
    transport: udpu
    token: 10000
}
""".strip()


def test_corosync_1():
    result = corosync.CoroSyncConfig(context_wrap(corosync_content))
    assert result.data['COROSYNC_OPTIONS'] == ""
    assert result.data['COROSYNC_INIT_TIMEOUT'] == "60"

    assert result.options == ''
    assert result.unparsed_lines == []


def test_corosync_conf():
    conf = corosync.CorosyncConf(context_wrap(COROSYNC_CONF))
    assert conf['totem']['token'][first].value == 10000
    assert conf['quorum']['provider'][first].value == 'corosync_votequorum'
    assert conf['nodelist']['node']['nodeid'][last].value == 3

    conf = corosync.CorosyncConf(context_wrap(COROSYNC_CONF_2))
    assert conf['totem']['version'][first].value == 2


def test_corosync_conf_empty():
    with pytest.raises(SkipException):
        assert corosync.CorosyncConf(context_wrap('')) is None


def test_doc_examples():
    failed, total = doctest.testmod(
        corosync,
        globs={'csconfig': corosync.CoroSyncConfig(context_wrap(corosync_content)),
               'corosync_conf': corosync.CorosyncConf(context_wrap(COROSYNC_CONF))}
    )
    assert failed == 0
