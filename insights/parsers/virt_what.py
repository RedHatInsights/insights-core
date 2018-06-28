'''
VirtWhat - Command ``virt-what``
================================

Parses the output of the ``virt-what`` command to check if the host is running
in a virtual machine.

Sample input::
    kvm

Examples:
    >>> vw = shared[VirtWhat]
    >>> vw.is_virtual
    True
    >>> vw.is_physical
    False
    >>> vw.generic
    'kvm'
    >>> 'aws' in vw
    False

Note:
    For ``virt-what-1.13-8`` or older on RHEL7, the command fails when running
    without an environment (or very restricted environment), and reports below
    error::

        virt-what: virt-what-cpuid-helper program not found in $PATH

'''
from .. import parser, CommandParser
from insights.specs import Specs

BAREMETAL = 'baremetal'


@parser(Specs.virt_what)
class VirtWhat(CommandParser):
    """
    Class for parsing ``virt-what`` command.

    Attributes:
        generic (str): The type of the virtual machine. 'baremetal' if physical machine.
        errors (list): List of the error information if any error occurs.
        specifics (list): List of the specific information if the command outputs.

    """

    def __init__(self, *args, **kwargs):
        self.generic = ''
        self.errors = []
        self.specifics = []
        super(VirtWhat, self).__init__(*args, **kwargs)

    def __contains__(self, name):
        """bool: Is this ``name`` found in the specific list?"""
        return name in [self.generic] + self.specifics

    @property
    def is_virtual(self):
        """
        bool: Is the host running in a virtual machine? None when something is
              wrong.
        """
        if not self.errors:
            return self.generic != BAREMETAL

    @property
    def is_physical(self):
        """
        bool: Is the host running in a physical machine? None when something is
              wrong.
        """
        if not self.errors:
            return self.generic == BAREMETAL

    def parse_content(self, content):
        if content:
            if len(content[0].split()) > 1:
                self.errors = [line for line in content]
            else:
                self.generic = content[0]
                self.specifics = [line for line in content[1:]]
        else:
            self.generic = BAREMETAL
