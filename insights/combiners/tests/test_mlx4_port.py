import doctest
from insights.tests import context_wrap
from insights.parsers.mlx4_port import Mlx4Port as Mlx4PortParser
from insights.combiners import mlx4_port
from insights.combiners.mlx4_port import Mlx4Port

MLX4_CONTENT_1 = """
ib
"""
MLX4_CONTENT_2 = """  line 1
  line 2"""

MLX4_PATH_1 = '/sys/bus/pci/devices/0000:0c:00.0/mlx4_port1'
MLX4_PATH_2 = '/sys/bus/pci/devices/0000:0c:00.0/mlx4_port2'


def test_mlx4_port():
    parser1 = Mlx4PortParser(context_wrap(MLX4_CONTENT_1, path=MLX4_PATH_1))
    parser2 = Mlx4PortParser(context_wrap(MLX4_CONTENT_2, path=MLX4_PATH_2))
    result = Mlx4Port([parser1, parser2])
    assert result is not None
    assert set(result.keys()) == set(['mlx4_port1', 'mlx4_port2'])
    assert result['mlx4_port1'] == ['ib']
    assert result['mlx4_port2'] == ['line 1', 'line 2']


def test_mlx4_docs():
    parser1 = Mlx4PortParser(context_wrap(MLX4_CONTENT_1, path=MLX4_PATH_1))
    parser2 = Mlx4PortParser(context_wrap(MLX4_CONTENT_2, path=MLX4_PATH_2))
    env = {'mlx4port': Mlx4Port([parser1, parser2])}
    failed, total = doctest.testmod(mlx4_port, globs=env)
    assert failed == 0
