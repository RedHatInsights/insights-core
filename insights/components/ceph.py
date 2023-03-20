"""
Component identifies Ceph Monitor
=================================

The ``Is*`` component in this module is valid if the
:py:class:`insights.combiners.ps.Ps` combiner indicates
the host is a Ceph monitor.  Otherwise, it raises a
:py:class:`insights.core.exceptions.SkipComponent` to prevent dependent components from
executing.

"""
from insights.combiners.ps import Ps
from insights.core.exceptions import SkipComponent
from insights.core.plugins import component


@component(Ps)
class IsCephMonitor(object):
    """
    This component uses ``Ps`` combiner to determine if the host is a Ceph
    monitor or not.  If not Ceph monitor, it raises ``SkipComponent``.

    Raises:
        SkipComponent: When it's not a Ceph monitor.
    """
    def __init__(self, ps):
        if not ps.search(COMMAND_NAME__contains='ceph-mon'):
            raise SkipComponent("Not Ceph Monitor")
