"""
IsSatellite611
==============

An ``IsSatellite*`` component is valid if the
:py:class:`insights.combiners.satellite_version.SatelliteVersion` combiner
indicates the major and minor Satellite versions represented by the component.
Otherwise, it raises a :py:class:`insights.core.dr.SkipComponent` to prevent
dependent components from executing.

In particular, an ``IsSatellite*`` component can be added as a dependency of a
parser to limit it to a given version.
"""
from insights.combiners.satellite_version import SatelliteVersion
from insights.core.dr import SkipComponent
from insights.core.plugins import component


class IsSatellite(object):
    """
    This component uses ``SatelliteVersion`` combiner to determine the
    Satellite major and minor versions. It checks if the major and minor
    versions matches the arguments, and raises ``SkipComponent`` when they
    do not match.

    Raises:
        SkipComponent: When Satellite major and minor versions do not match
            the arguments.
    """
    def __init__(self, sat, major_ver=None, minor_ver=None):
        if sat.major != major_ver or sat.minor != minor_ver:
            raise SkipComponent("Not Satellite {major_ver}.{minor_ver}".format(
                major_ver=major_ver, minor_ver=minor_ver))


@component(SatelliteVersion)
class IsSatellite611(IsSatellite):
    """
    This component uses ``SatelliteVersion`` combiner
    to determine the Satellite version. It checks if the Satellite version is 6.11,
    and raises ``SkipComponent`` when it isn't.

    Raises:
        SkipComponent: When Satellite version is not RHEL6.
    """
    def __init__(self, sat):
        super(IsSatellite611, self).__init__(sat, 6, 11)
