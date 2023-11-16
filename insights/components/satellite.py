"""
Components identify Satellite or Satellite Capsule
==================================================

An ``IsSatellite`` component is valid if the
:py:class:`insights.combiners.satellite_version.SatelliteVersion` combiner
indicates the host is a Satellite host, and also checks the Satellite major
or major and minor versions match the specified versions when they exist.
Otherwise, it raises a :py:class:`insights.core.exceptions.SkipComponent` to prevent
dependent components from executing.

An ``IsCapsule`` component is valid if the
:py:class:`insights.combiners.satellite_version.CapsuleVersion` combiner
indicates the host is a Satellite Capsule host, and also checks the Satellite
Capsule major or major and minor versions match the specified versions when
they exist. Otherwise, it raises a :py:class:`insights.core.exceptions.SkipComponent`
to prevent dependent components from executing.
"""
from insights.combiners.satellite_version import SatelliteVersion, CapsuleVersion
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import component


@component(SatelliteVersion)
class IsSatellite(object):
    """
    This component uses ``SatelliteVersion`` combiner to determine if the host
    is a Satellite host, and also if `major_ver` is passed, it checks if the
    curent satellite major version match the argument, and if both `major_ver`
    and `minor_ver` are passed, it checks if the current satellite major and
    minor versions match both the arguments, and raises ``SkipComponent`` when
    they do not match.

    Raises:
        ParseException: When only minor_ver specified.
        SkipComponent: When Satellite major or minor versions do not match
            the arguments.
    """
    def __init__(self, sat, major_ver=None, minor_ver=None):
        if major_ver is not None:
            if sat.major != major_ver:
                raise SkipComponent("Not a Satellite {major_ver} host.".format(
                    major_ver=major_ver))
            if minor_ver is not None:
                if sat.minor != minor_ver:
                    raise SkipComponent("Not a Satellite {major_ver}.{minor_ver} host.".format(
                        major_ver=major_ver, minor_ver=minor_ver))
        else:
            if minor_ver is not None:
                raise ParseException('Can not specify the minor_ver only.')


@component(CapsuleVersion)
class IsCapsule(object):
    """
    This component uses ``CapsuleVersion`` combiner to determine if the host
    is a Satellite Capsule host, and also if `major_ver` is passed, it checks
    if the curent capsule major version match the argument, and if both `major_ver`
    and `minor_ver` are passed, it checks if both the current capsule major and
    minor versions match both the arguments, and raises ``SkipComponent`` when
    they do not match.

    Raises:
        ParseException: When only minor_ver specified.
        SkipComponent: When the Satellite Capsule major or minor versions do
            not match the arguments.
    """
    def __init__(self, cap, major_ver=None, minor_ver=None):
        if major_ver is not None:
            if cap.major != major_ver:
                raise SkipComponent("Not a Satellite Capsule {major_ver} host.".format(
                    major_ver=major_ver))
            if minor_ver is not None:
                if cap.minor != minor_ver:
                    raise SkipComponent("Not a Satellite Capsule {major_ver}.{minor_ver} host.".format(
                        major_ver=major_ver, minor_ver=minor_ver))
        else:
            if minor_ver is not None:
                raise ParseException('Can not specify the minor_ver only.')


@component(SatelliteVersion)
class IsSatellite611(IsSatellite):
    """
    This component uses ``SatelliteVersion`` combiner
    to determine the Satellite version. It checks if the Satellite version is 6.11,
    and raises ``SkipComponent`` when it isn't.

    Raises:
        SkipComponent: When the Satellite version is not 6.11.
    """
    def __init__(self, sat):
        super(IsSatellite611, self).__init__(sat, 6, 11)


@component(SatelliteVersion)
class IsSatellite614AndLater(object):
    """
    This component uses ``SatelliteVersion`` combiner
    to determine the Satellite version. It checks if the Satellite version is 6.14 and later,
    and raises ``SkipComponent`` when it isn't.

    Raises:
        SkipComponent: When the Satellite version is earlier than 6.14.
    """
    def __init__(self, sat):
        if (sat.major < 6 or (sat.major == 6 and sat.minor < 14)):
            raise SkipComponent


@component(SatelliteVersion)
class IsSatelliteLessThan614(object):
    """
    This component uses ``SatelliteVersion`` combiner
    to determine the Satellite version. It checks if the Satellite version is 6.x and less than 6.14,
    and raises ``SkipComponent`` when it isn't.

    Raises:
        SkipComponent: When the Satellite version isn't 6.x or it's 6.14 and later.
    """
    def __init__(self, sat):
        if sat.major == 6 and sat.minor < 14:
            return
        raise SkipComponent
