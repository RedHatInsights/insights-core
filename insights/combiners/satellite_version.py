"""
Satellite Version
=================

Combiner for Satellite Version information. It uses the results of
the ``Satellite6Version`` parser and the ``InstalledRpms`` parser to determine
the satellite version

Below is the logic to determine the satellite version::

    1. For Satellite 6.1.x:
        a. Check the version information in below files at first
           - https://access.redhat.com/solutions/1392633

           File: /usr/share/foreman/lib/satellite/version.rb

        b. Check the version of package foreman, candlepin and katello, when
           the files listed in (a) are not found.
           - https://access.redhat.com/articles/1343683
             NOTE: There are some mistakes in the KCS, the versions in this
                   combiner are corrected according to the corresponding ERRATA.

                        Sat 6.0.8   Sat 6.1.10  Sat 6.1.11
           foreman      1.6.0.53    1.7.2.61    1.7.2.62
           candlepin    0.9.23      0.9.49.16   0.9.49.19
           katello      1.5.0       2.2.0       2.2.0

    2. For Satellite 6.2.x:
       - https://access.redhat.com/solutions/1392633

       Check the version of package `satellite` directly:

                        Sat 6.0.x   Sat 6.1.x   Sat 6.2.x
           satellite    -           -           6.2.x

    3. For Satellite 5.x
     - https://access.redhat.com/solutions/1224043
       NOTE: Because of `satellite-branding` is not deployed in Sat 5.0~5.2,
             and `satellite-schema` can also be used for checking the version,
             here checked `satellite-schema` instead of `satellite-branding`.

       Check the version of package satellite-schema directly:

                              Sat 5.0~5.2     Sat 5.3 ~
        rhn-satellite-schema  ok              -
        satellite-schema      -               ok


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
from insights.core.plugins import combiner
from insights.parsers.satellite_version import Satellite6Version as Sat6Ver
from insights.parsers.installed_rpms import InstalledRpms

SatelliteVersion = namedtuple(
        "SatelliteVersion",
        field_names=["full", "version", "release", "major", "minor"])
"""namedtuple: Type for storing the satellite version information."""


# Only track 6.0.x and 6.1.x. See https://access.redhat.com/articles/1343683
# But, there are some mistakes in the KCS, the versions in below map
# are corrected according to the corresponding ERRATA pages.
sat6_ver_map = {
        # Sat     foreman     candlepin   katello
        '6.0.8': ('1.6.0.53', '0.9.23', '1.5.0'),
        '6.1.1': ('1.7.2.33', '0.9.49.3', '2.2.0.14'),
        '6.1.2': ('1.7.2.36', '0.9.49.6', '2.2.0.16'),
        '6.1.3': ('1.7.2.43', '0.9.49.8', '2.2.0.16'),
        '6.1.4': ('1.7.2.46', '0.9.49.9', '2.2.0.16'),
        '6.1.5': ('1.7.2.49', '0.9.49.9', '2.2.0.16'),
        '6.1.6': ('1.7.2.50', '0.9.49.9', '2.2.0.17'),
        '6.1.7': ('1.7.2.53', '0.9.49.11', '2.2.0.17'),
        '6.1.8': ('1.7.2.55', '0.9.49.12', '2.2.0.19'),
        '6.1.9': ('1.7.2.56', '0.9.49.12', '2.2.0.19'),
        '6.1.10': ('1.7.2.61', '0.9.49.16', '2.2.0'),
        '6.1.11': ('1.7.2.62', '0.9.49.19', '2.2.0'),
        '6.1.12': ('1.7.2.63', '0.9.49.23', '2.2.0'),
}


def _parse_sat_versoin(version):
    ver_sp = version.split(".") if version else []
    major = int(ver_sp[0]) if ver_sp and ver_sp[0].isdigit() else None
    minor = int(ver_sp[1]) if len(ver_sp) > 1 and ver_sp[1].isdigit() else None
    return [major, minor]


@combiner(requires=[[Sat6Ver, InstalledRpms]])
def satellite_version(local, shared):
    """
    Check satellite_version and installed_rpms for satellite version
    information.

    Raises:
        Exception: If it's not a Satellite Server/Capsule or information is not
        enough to determine the satellite version.
    """
    # For Satellite 6.1.x, if satellite_version/version.rb is available:
    sat6_ver = shared.get(Sat6Ver)
    if sat6_ver and sat6_ver.version:
        return SatelliteVersion(sat6_ver.full, sat6_ver.version, None,
                                sat6_ver.major, sat6_ver.minor)

    rpms = shared.get(InstalledRpms)
    if rpms:
        # For Satellite 6.2.x, check the ``satellite`` package directly
        sat62_pkg = rpms.get_max('satellite')
        if sat62_pkg:
            version = sat62_pkg.version
            major, minor = _parse_sat_versoin(version)
            return SatelliteVersion(sat62_pkg.package, version,
                                    sat62_pkg.release, major, minor)

        # For Satellite 6.0.x/6.1.x, check the version of:
        # - foreman, candlepin and katello
        fman = rpms.get_max('foreman')
        cndp = rpms.get_max('candlepin')
        ktlo = rpms.get_max('katello')
        if fman and cndp and ktlo:
            for sat_ver, map_ver in sat6_ver_map.items():
                if all(pkg.version.startswith(mv)
                        for pkg, mv in zip([fman, cndp, ktlo], map_ver)):
                    major, minor = _parse_sat_versoin(sat_ver)
                    return SatelliteVersion(sat_ver, sat_ver, None, major, minor)

        # For Satellite 5.x
        sat5_pkg = rpms.get_max('satellite-schema')
        sat5_pkg = sat5_pkg if sat5_pkg else rpms.get_max('rhn-satellite-schema')
        if sat5_pkg:
            version = sat5_pkg.version
            major, minor = _parse_sat_versoin(version)
            return SatelliteVersion(sat5_pkg.package, version,
                                    sat5_pkg.release, major, minor)
        raise Exception("Not a Satellite Server/Capsule")
    raise Exception("Unable to determine satellite version.")
