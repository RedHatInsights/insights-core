"""
Mlx4Port - file ``/sys/bus/pci/devices/*/mlx4_port[0-9]``
=========================================================

This module provides processing for the contents of each file
matching the glob spec ``/sys/bus/pci/devices/*/mlx4_port[0-9]``.

Sample contents of this file looks like::

    ib

or::

    eth

Attributes:
    name (str): The mlx4 port name.
    contents (list): List of string values representing each line in
        the file.

Examples:
    >>> type(mlx4_port)
    <class 'insights.parsers.mlx4_port.Mlx4Port'>
    >>> mlx4_port.name
    'mlx4_port1'
    >>> mlx4_port.contents
    ['ib']
"""

from .. import parser, Parser
from insights.specs import Specs


@parser(Specs.mlx4_port)
class Mlx4Port(Parser):
    """
    Parse the contents of the mlx4_port file
    """
    def parse_content(self, content):
        self.name = self.file_name
        self.contents = [line.strip() for line in content]
