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
