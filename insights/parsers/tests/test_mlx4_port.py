import doctest
from insights.tests import context_wrap
from insights.parsers import mlx4_port
from insights.parsers.mlx4_port import Mlx4Port

MLX4_CONTENT = """
ib
"""

MLX4_CONTENT_ML = """  line 1
  line 2"""

MLX4_PATH = '/sys/bus/pci/devices/0000:0c:00.0/mlx4_port1'


def test_mlx4_port():
    result = Mlx4Port(context_wrap(MLX4_CONTENT, path=MLX4_PATH))
    assert result.name == 'mlx4_port1'
    assert result.contents == ['ib']
    result = Mlx4Port(context_wrap(MLX4_CONTENT_ML, path=MLX4_PATH))
    assert result.name == 'mlx4_port1'
    assert result.contents == ['line 1', 'line 2']


def test_mlx4_docs():
    env = {'mlx4_port': Mlx4Port(context_wrap(MLX4_CONTENT, path=MLX4_PATH))}
    failed, total = doctest.testmod(mlx4_port, globs=env)
    assert failed == 0
