from insights.components.satellite_version import IsSatellite611
from insights.combiners.satellite_version import SatelliteVersion
from insights.parsers.installed_rpms import InstalledRpms
from insights.tests import context_wrap
from insights.core.dr import SkipComponent
import pytest

SUPPORTED_SATELLITE_VERSION_610_INSTALLED_RPMS = """
ConsoleKit-0.4.1-3.el6.x86_64                               Wed Sep 17 11:34:25 2014
kernel-2.6.32-573.el6.x86_64                                Wed May 18 14:17:17 2016
satellite-6.10.0.11-1.el7sat.noarch                          Wed May 18 14:16:25 2016
""".strip()

SUPPORTED_SATELLITE_VERSION_611_INSTALLED_RPMS = """
ConsoleKit-0.4.1-3.el6.x86_64                               Wed Sep 17 11:34:25 2014
kernel-2.6.32-573.el6.x86_64                                Wed May 18 14:17:17 2016
satellite-6.11.0-1.el7sat.noarch                             Wed May 18 14:16:25 2016
""".strip()


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
    assert "Not Satellite 6.11" in str(e)
