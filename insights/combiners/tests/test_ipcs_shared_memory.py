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

from insights.parsers import ParseException
from insights.parsers.ipcs import IpcsM, IpcsMP
from insights.combiners import ipcs_shared_memory
from insights.combiners.ipcs_shared_memory import IpcsSharedMemory
from insights.tests import context_wrap
import doctest
import pytest

IPCS_M = """
------ Shared Memory Segments --------
key        shmid      owner      perms      bytes      nattch     status
0x0052e2c1 0          postgres   600        37879808   26
0x0052e2c2 1          postgres   600        41222144   24
""".strip()

IPCS_M_P = """
------ Shared Memory Creator/Last-op --------
shmid      owner      cpid       lpid
0          postgres   1833       23566
1          postgres   1105       9882
""".strip()

IPCS_M_P_AB = """
------ Shared Memory Creator/Last-op --------
shmid      owner      cpid       lpid
0          postgres   1833       23566
""".strip()


def test_ipcs_shm():
    shm = IpcsM(context_wrap(IPCS_M))
    shmp = IpcsMP(context_wrap(IPCS_M_P))
    rst = IpcsSharedMemory(shm, shmp)
    assert rst.get_shm_size_of_pid('1833') == 37879808
    assert rst.get_shm_size_of_pid('33') == 0


def test_ipcs_shm_abnormal():
    shm = IpcsM(context_wrap(IPCS_M))
    shmp = IpcsMP(context_wrap(IPCS_M_P_AB))
    with pytest.raises(ParseException) as pe:
        IpcsSharedMemory(shm, shmp)
    assert "The output of 'ipcs -m' doesn't match with 'ipcs -m -p'." in str(pe)


def test_doc_examples():
    env = {
            'ism': IpcsSharedMemory(
                        IpcsM(context_wrap(IPCS_M)),
                        IpcsMP(context_wrap(IPCS_M_P)))
          }
    failed, total = doctest.testmod(ipcs_shared_memory, globs=env)
    assert failed == 0
