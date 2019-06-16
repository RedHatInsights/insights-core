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

from insights.parsers import cpuset_cpus
from insights.tests import context_wrap


CPUSET_CPU = """
0,2-4,7
""".strip()


def test_init_process_cgroup():
    cpusetinfo = cpuset_cpus.CpusetCpus(context_wrap(CPUSET_CPU))
    assert cpusetinfo.cpu_set == ["0", "2", "3", "4", "7"]
    assert cpusetinfo.cpu_number == 5
