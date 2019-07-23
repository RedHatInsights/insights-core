"""
Mlx4Port Combiner for the Mlx4Port Parser
=========================================

Combiner for the :class:`insights.parsers.mlx4_port.Mlx4Port` parser.

This parser is multioutput, one parser instance for each port
file.  This combiner puts all of them back together and presents
them as a dict where the keys are the port names, and the contents
of the port name file are the lines in each file stored as a list.

This class inherits all methods and attributes from the ``dict`` object.

Examples:
    >>> type(mlx4port)
    <class 'insights.combiners.mlx4_port.Mlx4Port'>
    >>> mlx4port['mlx4_port1']
    ['ib']
    >>> sorted(mlx4port.keys())
    ['mlx4_port1', 'mlx4_port2']

"""

from .. import combiner
from insights.parsers.mlx4_port import Mlx4Port as Mlx4PortParser


@combiner(Mlx4PortParser)
class Mlx4Port(dict):
    """
    Combiner for the mlx4_port parser.
    """
    def __init__(self, mlx4_port):
        super(Mlx4Port, self).__init__()
        for port in mlx4_port:
            self.update({port.name: port.contents})
