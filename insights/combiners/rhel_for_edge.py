"""
Combiner for edge computing systems
===================================
This combiner uses the following parsers to determine if the system is an edge computing systems.

* :py:class:`insights.parsers.installed_rpms.InstalledRpms`
* :py:class:`insights.parsers.cmdline.CmdLine`
* :py:class:`insights.parsers.systemd.unitfiles.ListUnits`
* :py:class:`insights.parsers.redhat_release.RedhatRelease`
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.cmdline import CmdLine
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.systemd.unitfiles import ListUnits
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.rpm_ostree_status import RpmOstreeStatus


@combiner(ListUnits, optional=[RpmOstreeStatus, InstalledRpms, CmdLine, RedhatRelease])
class RhelForEdge(object):
    """Combiner for checking if the system is an edge computing system. Edge
    computing as well as the Red Hat CoreOS packages are managed via rpm-ostree.
    Use the string "Red Hat Enterprise Linux release" from
    ``/etc/redhat-release`` to determine an edge computing system. The Red Hat
    CoreOS system will have "Red Hat Enterprise Linux CoreOS release" as the
    string.

    .. note::
        RHEL for EDGE is available and supported since RHEL 8.3.

    When an edge computing system (created from online console edge image) is
    configured to use the automated management, the output of ``rhc status`` is
    as below::

            Connection status for <HOST>:
            - Connected to Red Hat Subscription Management
            - The Red Hat connector daemon is active

    The ``rhcd.service`` running on an edge computing system signifies that it
    is configured to use the automated management.

    Attributes:
        is_edge (bool): True when it is an edge computing system
        is_automated (bool): True when the the edge computing system is configured to use automated management

    .. note::
        It is possible to run ``rhcd.service`` on the edge systems created
        from the cockpit edge image. The **is_automated** attribute is only for
        front-end resolution surface. It is used when the edge image is from
        the online console.

    Examples:
        >>> type(rhel_for_edge_obj)
        <class 'insights.combiners.rhel_for_edge.RhelForEdge'>
        >>> rhel_for_edge_obj.is_edge
        True
        >>> rhel_for_edge_obj.is_automated
        True

    """

    def __init__(self, units, rpmostreestatus, rpms, cmdline, redhatrelease):
        self.is_edge = False
        self.is_automated = False
        if rpmostreestatus:
            origin = rpmostreestatus.query.deployments.origin
            origin_check = [item.value.endswith("edge") for item in origin]
            if origin_check and all(origin_check):
                self.is_edge = True
                if units.is_running("rhcd.service"):
                    self.is_automated = True
        elif rpms and cmdline and redhatrelease:
            if ('rpm-ostree' in rpms and 'yum' not in rpms) and \
                    ('ostree' in cmdline) and \
                    ("red hat enterprise linux release" in redhatrelease.raw.lower()):
                self.is_edge = True
                if units.is_running("rhcd.service"):
                    self.is_automated = True
        else:
            raise SkipComponent("Unable to determine if this system is created from an edge image.")
