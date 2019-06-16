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
from insights.parsers import SkipException
from insights.parsers import numa_cpus
from insights.parsers.numa_cpus import NUMACpus
from insights.tests import context_wrap

NODE0_PATH = "/sys/devices/system/node/node0/cpulist"
NODE1_PATH = "/sys/devices/system/node/node1/cpulist"
NODE0_PATH_NO = ""

NODE0_CPULIST_RANGE = """
0-6,14-20
""".strip()

NODE1_CPULIST_RANGE = """
""".strip()

NODE0_CPULIST_RANGE_1 = """
0-3
""".strip()
NODE1_CPULIST_RANGE_2 = """
4-7
""".strip()

NODE0_CPULIST = """
0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46
""".strip()

NODE1_CPULIST = """
1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47
""".strip()


def test_cpulist_node0():
    context = context_wrap(NODE1_CPULIST, NODE1_PATH)
    cpu_obj = NUMACpus(context)
    assert cpu_obj.numa_node_details() == {'numa_node_range': ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21', '23', '25', '27', '29', '31', '33', '35', '37', '39', '41', '43', '45', '47'], 'numa_node_name': 'node1', 'total_cpus': 24}
    assert cpu_obj.numa_node_name == 'node1'
    assert len(cpu_obj.numa_node_cpus) == 24
    assert cpu_obj.total_numa_node_cpus == 24

    context = context_wrap(NODE0_CPULIST_RANGE, NODE0_PATH)
    cpu_obj = NUMACpus(context)
    assert cpu_obj.numa_node_details() == {'numa_node_range': ['0-6', '14-20'], 'numa_node_name': 'node0', 'total_cpus': 14}
    assert cpu_obj.numa_node_name == 'node0'
    assert cpu_obj.numa_node_cpus == ['0-6', '14-20']
    assert cpu_obj.total_numa_node_cpus == 14

    context = context_wrap(NODE1_CPULIST_RANGE_2, NODE1_PATH)
    cpu_obj = NUMACpus(context)
    assert cpu_obj.numa_node_details() == {'numa_node_range': ['4-7'], 'numa_node_name': 'node1', 'total_cpus': 4}
    assert cpu_obj.numa_node_name == 'node1'
    assert cpu_obj.numa_node_cpus == ['4-7']
    assert cpu_obj.total_numa_node_cpus == 4

    with pytest.raises(SkipException) as exc:
        cpu_obj = NUMACpus(context_wrap(NODE1_CPULIST_RANGE, NODE1_PATH))
        assert cpu_obj.numa_node_name == 'node1'
        assert not cpu_obj.total_numa_node_cpus
    assert 'No Contents' in str(exc)


def test_numa_node_doc_examples():
    env = {'numa_cpus_obj': NUMACpus(context_wrap(NODE0_CPULIST_RANGE, NODE0_PATH))}
    failed, total = doctest.testmod(numa_cpus, globs=env)
    assert failed == 0
