"""
LsOriginLocalVolumePods - command ``ls -l /var/lib/origin/openshift.local.volumes/pods``
========================================================================================
"""

from insights.specs import Specs
from insights import FileListing, parser, CommandParser
from insights.util import deprecated


@parser(Specs.ls_origin_local_volumes_pods)
class LsOriginLocalVolumePods(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSla` instead.

    Class to parse the output of command ``ls -l /var/lib/origin/openshift.local.volumes/pods``.
    See ``FileListing`` class for additional information.

    The typical content is::

        total 0
        drwxr-x---. 5 root root 71 Oct 18 23:20 5946c1f644096161a1242b3de0ee5875
        drwxr-x---. 5 root root 71 Oct 18 23:24 6ea3d5cd-d34e-11e8-a142-001a4a160152
        drwxr-x---. 5 root root 71 Oct 18 23:31 77d6d959-d34f-11e8-a142-001a4a160152
        drwxr-x---. 5 root root 71 Oct 18 23:24 7ad952a0-d34e-11e8-a142-001a4a160152
        drwxr-x---. 5 root root 71 Oct 18 23:24 7b63e8aa-d34e-11e8-a142-001a4a160152


    Examples:

        >>> ls_origin_local_volumes_pods.pods
        ['5946c1f644096161a1242b3de0ee5875', '6ea3d5cd-d34e-11e8-a142-001a4a160152', '77d6d959-d34f-11e8-a142-001a4a160152', '7ad952a0-d34e-11e8-a142-001a4a160152', '7b63e8aa-d34e-11e8-a142-001a4a160152']

    Attributes:
        pods (List): The list of pods uid under the directory /var/lib/origin/openshift.local.volumes/pods
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsOriginLocalVolumePods, "Please use the :class:`insights.parsers.ls.LSla` instead.", "3.5.0")
        super(LsOriginLocalVolumePods, self).__init__(*args, **kwargs)

    @property
    def pods(self):
        return self.dirs_of("/var/lib/origin/openshift/local/volumes/pods")
