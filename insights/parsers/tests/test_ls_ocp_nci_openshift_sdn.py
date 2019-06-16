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

from insights.parsers import ls_ocp_cni_openshift_sdn
from insights.parsers.ls_ocp_cni_openshift_sdn import LsOcpCniOpenshiftSdn
from insights.tests import context_wrap

LS_CNI_OPENSHIFT_SDN = """
total 52
-rw-r--r--. 1 root root 64 Aug  5 23:26 10.130.0.102
-rw-r--r--. 1 root root 64 Aug  5 23:26 10.130.0.103
-rw-r--r--. 1 root root 64 Aug  6 22:52 10.130.0.116
-rw-r--r--. 1 root root 64 Aug  6 22:52 10.130.0.117
-rw-r--r--. 1 root root 64 Aug  5 06:59 10.130.0.15
-rw-r--r--. 1 root root 64 Aug  5 07:02 10.130.0.20
-rw-r--r--. 1 root root 12 Aug  6 22:52 last_reserved_ip.0
""".strip()


def test_ls_ocp_cni_openshift_sdn():
    ls_ocp_cni_openshift_sdn = LsOcpCniOpenshiftSdn(
        context_wrap(LS_CNI_OPENSHIFT_SDN, path='insights_commands/ls_-l_.var.lib.cni.networks.openshift-sdn'))
    assert len(ls_ocp_cni_openshift_sdn.files_of("/var/lib/cni/networks/openshift-sdn")) == 7
    assert ls_ocp_cni_openshift_sdn.files_of("/var/lib/cni/networks/openshift-sdn") == ['10.130.0.102', '10.130.0.103',
                                                                                        '10.130.0.116', '10.130.0.117',
                                                                                        '10.130.0.15', '10.130.0.20',
                                                                                        'last_reserved_ip.0']


def test_ls_ocp_cni_openshift_sdn_doc_examples():
    env = {
        'ls_ocp_cni_openshift_sdn': LsOcpCniOpenshiftSdn(
            context_wrap(LS_CNI_OPENSHIFT_SDN, path='insights_commands/ls_-l_.var.lib.cni.networks.openshift-sdn')),
    }
    failed, total = doctest.testmod(ls_ocp_cni_openshift_sdn, globs=env)
    assert failed == 0
