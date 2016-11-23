"""
satellite_version
=================

Shared reducer for Satellite Version information. It uses the results of
the ``Satellite6Version`` mapper and the ``InstalledRpms`` mapper to determine
the satellite version

Below is the logic to determine the satellite version
    1. For Satellite 6.x
     - https://access.redhat.com/articles/1343683
     - https://access.redhat.com/solutions/1392633

        > For Satellite 6.1.x
        a. Check the version information in below files at first
           - satellite_version
           - /usr/share/foreman/lib/satellite/version.rb
        b. Check the version of package foreman, when the files listed in (a)
           are not found.
                        Sat 6.0.x   Sat 6.1.x   Sat 6.2.x
           foreman      1.6.x       1.7.2.x     1.11.0.x

        > For Satellite 6.2.x
        a. Check the version of package satellite
                        Sat 6.0.x   Sat 6.1.x   Sat 6.2.x
           satellite    -           -           6.2.x

    2. For Satellite 5.x
     - https://access.redhat.com/solutions/1224043

     Check the version of package satellite-schema directly
                           Sat 5.0~5.2     Sat 5.3~5.7
     rhn-satellite-schema  ok              -
     satellite-schema      -               ok

     * Because of satellite-branding is not deployed in Sat 5.0~5.2, and
     satellite-schema can also be used for checking the version, so here we
     checked satellite-schema instead of satellite-branding

Examples:
    >>> sat_ver = shared[satellite_version]
    >>> sat_ver.major
    6
    >>> sat_ver.minor
    2
    >>> sat_ver.version
    '6.2.2'
    >>> sat_ver.full
    '6.2.2.1-1.0.el7sat'
    >>> sat_ver.release
    '1.0.el7sat'

"""

from collections import namedtuple
from falafel.core.plugins import reducer
from falafel.mappers.satellite_version import Satellite6Version as Sat6Ver
from falafel.mappers.installed_rpms import InstalledRpms

SatelliteVersion = namedtuple(
        "SatelliteVersion",
        field_names=["full", "version", "release", "major", "minor"])
"""namedtuple: Type for storing the satellite version information."""

foreman_sat6_ver_map = {
    '1.6.0.53': '6.0.8',
    '1.7.2.33': '6.1.1',
    '1.7.2.36': '6.1.2',
    '1.7.2.43': '6.1.3',
    '1.7.2.46': '6.1.4',
    '1.7.2.49': '6.1.5',
    '1.7.2.50': '6.1.6',
    '1.7.2.53': '6.1.7',
    '1.7.2.55': '6.1.8',
    '1.7.2.56': '6.1.9',
    '1.7.2.61': '6.1.10',
    '1.11.0.49': '6.2',
    '1.11.0.51': '6.2.1',
    '1.11.0.53': '6.2.2',
}


def _parse_sat_versoin(version):
    ver_sp = version.split(".") if version else []
    major = int(ver_sp[0]) if ver_sp and ver_sp[0].isdigit() else None
    minor = int(ver_sp[1]) if len(ver_sp) > 1 and ver_sp[1].isdigit() else None
    return [major, minor]


@reducer(requires=[[Sat6Ver, InstalledRpms]], shared=True)
def satellite_version(local, shared):
    """
    Check satellite_version and installed_rpms for satellite version
    information.

    """
    # For Satellite 6.1.x (satellite_version/version.rb is available)
    sat6_ver = shared.get(Sat6Ver)
    if sat6_ver and sat6_ver.version:
        return SatelliteVersion(sat6_ver.full, sat6_ver.version, None,
                                sat6_ver.major, sat6_ver.minor)

    rpms = shared.get(InstalledRpms)
    if rpms:
        # For Satellite 6.2.x
        sat62_pkg = rpms.get_max('satellite')
        if sat62_pkg:
            version = sat62_pkg.version
            major, minor = _parse_sat_versoin(version)
            return SatelliteVersion(sat62_pkg.package, version,
                                    sat62_pkg.release, major, minor)

        # For Satellite 6.0.x/6.1.x
        fman_pkg = rpms.get_max('foreman')
        sat6_ver = foreman_sat6_ver_map.get(fman_pkg.version) if fman_pkg else None
        if sat6_ver:
            major, minor = _parse_sat_versoin(sat6_ver)
            return SatelliteVersion(sat6_ver, sat6_ver, None, major, minor)

        # For Satellite 5.0
        sat5_pkg = rpms.get_max('satellite-schema')
        sat5_pkg = sat5_pkg if sat5_pkg else rpms.get_max('rhn-satellite-schema')
        if sat5_pkg:
            version = sat5_pkg.version
            major, minor = _parse_sat_versoin(version)
            return SatelliteVersion(sat5_pkg.package, version,
                                    sat5_pkg.release, major, minor)
