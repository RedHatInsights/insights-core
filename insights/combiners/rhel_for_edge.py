"""
Combiner for edge computing systems
===================================
This combiner uses the following parsers to determine if the system is an edge computing systems.

* :py:class:`insights.parsers.installed_rpms.InstalledRpms`
* :py:class:`insights.parsers.cmdline.CmdLine`
* :py:class:`insights.parsers.systemd.unitfiles.ListUnits`
* :py:class:`insights.parsers.redhat_release.RedhatRelease`
"""
from insights.core.plugins import combiner
from insights.parsers.cmdline import CmdLine
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.systemd.unitfiles import ListUnits
from insights.parsers.redhat_release import RedhatRelease


@combiner(InstalledRpms, CmdLine, ListUnits, RedhatRelease)
class RhelForEdge(object):
    """
    Combiner for checking if the system is an edge computing systems.
    Edge computing system packages are managed via rpm-ostree.
    Red Hat CoreOS is also managed via rpm-ostree, use the string "Red Hat Enterprise Linux release"
    from "/etc/redhat-release" to determine if it is an edge computing system as it is
    "Red Hat Enterprise Linux CoreOS release" on RedHat CoreOs.

    .. note::
        RHEL for EDGE is available and supported since RHEL 8.3.

    When an edge computing system created from online console edge image is configured to use
    automated management, the output of "rhc status" is the following::

            Connection status for test.localhost:
            - Connected to Red Hat Subscription Management
            - The Red Hat connector daemon is active

    If a system can upload insights archive, it must be connected to Red Hat Subscription Management,
    rhcd service running means an edge computing system is configured to use automated management.

    Attributes:
        is_edge (bool): True when it is an edge computing system
        is_automated (bool): True when the the edge computing system is configured to use automated management

    .. note::
        It is also able to run rhcd service on the edge systems created from cockpit edge image,
        "is_automated" is only for front-end resolution surface, it is used when customers determine that
        the image is from online console.

    Examples:
        >>> type(rhel_for_edge_obj)
        <class 'insights.combiners.rhel_for_edge.RhelForEdge'>
        >>> rhel_for_edge_obj.is_edge
        True
        >>> rhel_for_edge_obj.is_automated
        True
    """

    def __init__(self, rpms, cmdline, units, redhatrelease):
        self.is_edge = False
        self.is_automated = False

        if ('rpm-ostree' in rpms and 'yum' not in rpms) and \
                ('ostree' in cmdline) and \
                ("red hat enterprise linux release" in redhatrelease.raw.lower()):
            self.is_edge = True
            if units.is_running("rhcd.service"):
                self.is_automated = True
