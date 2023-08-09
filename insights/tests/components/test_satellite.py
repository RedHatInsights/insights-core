import pytest

from insights.combiners.satellite_version import SatelliteVersion, CapsuleVersion
from insights.components.satellite import IsCapsule, IsSatellite, IsSatellite611
from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers.installed_rpms import InstalledRpms
from insights.tests import context_wrap


NOT_SATELITE_RPMS = """
ConsoleKit-0.4.1-3.el6.x86_64                               Wed Sep 17 11:34:25 2014
kernel-2.6.32-573.el6.x86_64                                Wed May 18 14:17:17 2016
""".strip()

SUPPORTED_SATELLITE_VERSION_610_INSTALLED_RPMS = """
ConsoleKit-0.4.1-3.el6.x86_64                               Wed Sep 17 11:34:25 2014
kernel-2.6.32-573.el6.x86_64                                Wed May 18 14:17:17 2016
satellite-6.10.0.11-1.el7sat.noarch                         Wed May 18 14:16:25 2016
""".strip()

SUPPORTED_SATELLITE_VERSION_611_INSTALLED_RPMS = """
ConsoleKit-0.4.1-3.el6.x86_64                               Wed Sep 17 11:34:25 2014
kernel-2.6.32-573.el6.x86_64                                Wed May 18 14:17:17 2016
satellite-6.11.0-1.el7sat.noarch                            Wed May 18 14:16:25 2016
""".strip()

SUPPORTED_SATELLITE_CAPSULE_VERSION_69_INSTALLED_RPMS = """
satellite-capsule-6.9.0-1.el7sat.noarch                     Thu Jan  9 12:26:31 2020
satellite-installer-6.9.0.4-1.el7sat.noarch                 Thu Jan  9 12:26:26 2020
""".strip()

SUPPORTED_SATELLITE_CAPSULE_VERSION_610_INSTALLED_RPMS = """
satellite-capsule-6.10.3-1.el7sat.noarch                     Thu Jan  9 12:26:31 2020
satellite-installer-6.10.3-1.el7sat.noarch                   Thu Jan  9 12:26:26 2020
""".strip()


# IsSatellite test
def test_is_satellite():
    rpms = InstalledRpms(context_wrap(SUPPORTED_SATELLITE_VERSION_610_INSTALLED_RPMS))
    sat_ver = SatelliteVersion(rpms, None)
    result = IsSatellite(sat_ver)
    assert result is not None
    result_6 = IsSatellite(sat_ver, 6)
    assert result_6 is not None
    result_610 = IsSatellite(sat_ver, 6, 10)
    assert result_610 is not None


def test_is_satellite_except():
    rpms = InstalledRpms(context_wrap(NOT_SATELITE_RPMS))
    with pytest.raises(SkipComponent):
        SatelliteVersion(rpms, None)

    rpms = InstalledRpms(context_wrap(SUPPORTED_SATELLITE_VERSION_610_INSTALLED_RPMS))
    sat_ver = SatelliteVersion(rpms, None)
    with pytest.raises(ParseException):
        IsSatellite(sat_ver, None, 11)
    with pytest.raises(SkipComponent):
        IsSatellite(sat_ver, 5)
    with pytest.raises(SkipComponent):
        IsSatellite(sat_ver, 6, 11)


# IsCapsule test
def test_is_satellite_capsule():
    rpms = InstalledRpms(context_wrap(SUPPORTED_SATELLITE_CAPSULE_VERSION_69_INSTALLED_RPMS))
    cap_ver = CapsuleVersion(rpms, None)
    result = IsCapsule(cap_ver)
    assert result is not None
    result_6 = IsCapsule(cap_ver, 6)
    assert result_6 is not None
    result_69 = IsCapsule(cap_ver, 6, 9)
    assert result_69 is not None


def test_is_capsule_except():
    rpms = InstalledRpms(context_wrap(NOT_SATELITE_RPMS))
    with pytest.raises(SkipComponent):
        CapsuleVersion(rpms, None)
    rpms = InstalledRpms(context_wrap(SUPPORTED_SATELLITE_CAPSULE_VERSION_610_INSTALLED_RPMS))
    cap_ver = CapsuleVersion(rpms, None)
    with pytest.raises(ParseException):
        IsCapsule(cap_ver, None, 11)
    with pytest.raises(SkipComponent):
        IsCapsule(cap_ver, 5)
    with pytest.raises(SkipComponent):
        IsCapsule(cap_ver, 6, 11)


# Satellite611 Tests
def test_is_satellite611():
    rpms = InstalledRpms(context_wrap(SUPPORTED_SATELLITE_VERSION_611_INSTALLED_RPMS))
    sat_ver = SatelliteVersion(rpms, None)
    result = IsSatellite611(sat_ver)
    assert isinstance(result, IsSatellite611)


def test_not_satellite611():
    rpms = InstalledRpms(context_wrap(SUPPORTED_SATELLITE_VERSION_610_INSTALLED_RPMS))
    sat_ver = SatelliteVersion(rpms, None)
    with pytest.raises(SkipComponent) as e:
        IsSatellite611(sat_ver)
    assert "Not a Satellite 6.11" in str(e)
