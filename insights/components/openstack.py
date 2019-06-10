"""
IsOpenStackCompute
==================

The ``IsOpenStackCompute`` component uses ``PsAuxcww`` parser to determine
OpenStack Compute node. It checks if 'nova-compute' process exist, if not raises
``SkipComponent`` so that the dependent component will not fire. Can be added as
a dependency of a parser so that the parser only fires if the
``IsIsOpenStackCompute`` dependency is met.
"""
from insights.core.plugins import component
from insights.parsers.ps import PsAuxcww
from insights.core.dr import SkipComponent


@component(PsAuxcww)
class IsOpenStackCompute(object):
    """The ``IsOpenStackCompute`` component uses ``PsAuxcww`` parser to determine
    OpenStack Compute node. It checks if ``nova-compute`` process exist, if not
    raises ``SkipComponent``.

    Raises:
        SkipComponent: When ``nova-compute`` process does not exist.
    """
    def __init__(self, ps):
        if 'nova-compute' not in ps.running:
            raise SkipComponent('Not OpenStack Compute node')
