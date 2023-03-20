"""
Components identify system type with regard to virtualization
=============================================================

The ``IsBareMetal`` component in this module is valid if the
:py:class:`insights.combiners.virt_what.VirtWhat` combiner indicates
the host is bare metal.
"""
from insights.combiners.virt_what import VirtWhat
from insights.core.exceptions import SkipComponent
from insights.core.plugins import component


@component(VirtWhat)
class IsBareMetal(object):
    """
    This component uses ``VirtWhat`` combiner to determine the virtualization type.
    It checks if the system is bare metal, otherwise it raises ``SkipComponent``.

    Raises:
        SkipComponent: When system is a virtual machine.
    """
    def __init__(self, virt):
        if virt.is_virtual:
            raise SkipComponent("Not a bare metal system.")
