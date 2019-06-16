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

from insights.tests import context_wrap
from insights.parsers.mlx4_port import Mlx4Port

MLX4_PORT = """
/sys/bus/pci/devices/0000:0c:00.0/mlx4_port1
ib
/sys/bus/pci/devices/0000:0c:00.0/mlx4_port2
eth
"""


def test_mlx4_port():
    result = Mlx4Port(context_wrap(MLX4_PORT))
    assert result.port_val == {'mlx4_port1': 'ib', 'mlx4_port2': 'eth'}
    assert result.port_val['mlx4_port1'] == 'ib'
    assert len(result.port_val) == 2
