from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.satellite_version import Satellite6Version
from insights.combiners import satellite_version
from insights.combiners.satellite_version import SatelliteVersion, CapsuleVersion
from insights.tests import context_wrap
from insights import SkipComponent
import pytest
import doctest


installed_rpms_5 = """
satellite-branding-5.5.0.22-1.el6sat.noarch                 Wed May 18 14:50:17 2016
satellite-doc-indexes-5.6.0-2.el6sat.noarch                 Wed May 18 14:47:49 2016
satellite-repo-5.6.0.3-1.el6sat.noarch                      Wed May 18 14:37:34 2016
satellite-schema-5.6.0.10-1.el6sat.noarch                   Wed May 18 14:53:03 2016
satyr-0.16-2.el6.x86_64                                     Wed May 18 14:16:08 2016
scdb-1.15.8-1.el6sat.noarch                                 Wed May 18 14:48:14 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el6.x86_64                                     Wed May 18 14:16:25 2016
"""

installed_rpms_60 = """
foreman-1.6.0.53-1.el7sat.noarch                            Wed May 18 14:16:25 2016
candlepin-0.9.23.11-1.el7.noarch                            Wed May 18 14:16:25 2016
katello-1.5.0.2-1.el7.noarch                                Wed May 18 14:16:25 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el6.x86_64                                     Wed May 18 14:16:25 2016
"""

installed_rpms_61 = """
foreman-1.7.2.53-1.el7sat.noarch                            Wed May 18 14:16:25 2016
candlepin-0.9.49.11-1.el7.noarch                            Wed May 18 14:16:25 2016
katello-2.2.0.17-1.el7.noarch                               Wed May 18 14:16:25 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el6.x86_64                                     Wed May 18 14:16:25 2016
"""

installed_rpms_62 = """
foreman-1.11.0.53-1.el7sat.noarch                           Wed May 18 14:16:25 2016
scl-utils-20120927-27.el7_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el7.x86_64                                     Wed May 18 14:16:25 2016
satellite-6.2.0.11-1.el7sat.noarch                          Wed May 18 14:16:25 2016
"""

installed_rpms_62_cap = """
scl-utils-20120927-27.el7_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el7.x86_64                                     Wed May 18 14:16:25 2016
satellite-capsule-6.2.0.11-1.el7sat.noarch                  Wed May 18 14:16:25 2016
"""

satellite_version_rb = """
COMMAND> cat /usr/share/foreman/lib/satellite/version.rb

module Satellite
  VERSION = "6.1.3"
end
"""

no_sat = """
scdb-1.15.8-1.el6sat.noarch                                 Wed May 18 14:48:14 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el6.x86_64                                     Wed May 18 14:16:25 2016
"""

installed_rpms_6110 = """
foreman-1.7.2.61-1.el7sat.noarch                            Wed May 18 14:16:25 2016
candlepin-0.9.49.16-1.el7.noarch                            Wed May 18 14:16:25 2016
katello-2.2.0.19-1.el7.noarch                               Wed May 18 14:16:25 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
"""

installed_rpms_6111 = """
foreman-1.7.2.62-1.el7sat.noarch                            Wed May 18 14:16:25 2016
candlepin-0.9.49.19-1.el7.noarch                            Wed May 18 14:16:25 2016
katello-2.2.0.19-1.el7.noarch                               Wed May 18 14:16:25 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
"""

installed_rpms_611x_confilct = """
foreman-1.7.2.61-1.el7sat.noarch                            Wed May 18 14:16:25 2016
candlepin-0.9.54.10-1.el7.noarch                            Wed May 18 14:16:25 2016
katello-2.3.0.19-1.el7.noarch                               Wed May 18 14:16:25 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
"""


def test_get_sat5_version():
    rpms = InstalledRpms(context_wrap(installed_rpms_5))
    expected = ('satellite-schema-5.6.0.10-1.el6sat',
                '5.6.0.10', '1.el6sat', 5, 6)
    result = SatelliteVersion(rpms, None)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]


def test_get_sat61_version():
    rpms = InstalledRpms(context_wrap(installed_rpms_61))
    expected = ('6.1.7', '6.1.7', None, 6, 1)
    result = SatelliteVersion(rpms, None)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]

    sat = Satellite6Version(context_wrap(satellite_version_rb))
    expected = ('6.1.3', '6.1.3', None, 6, 1)
    result = SatelliteVersion(rpms, sat)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]

    rpms = InstalledRpms(context_wrap(installed_rpms_6110))
    expected = ('6.1.10', '6.1.10', None, 6, 1)
    result = SatelliteVersion(rpms, None)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]

    rpms = InstalledRpms(context_wrap(installed_rpms_6111))
    expected = ('6.1.11', '6.1.11', None, 6, 1)
    result = SatelliteVersion(rpms, None)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]


def test_get_sat60():
    rpms = InstalledRpms(context_wrap(installed_rpms_60))
    expected = ('6.0.8', '6.0.8', None, 6, 0)
    result = SatelliteVersion(rpms, None)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]


def test_get_sat61_version_both():
    rpms = InstalledRpms(context_wrap(installed_rpms_61))
    sat = Satellite6Version(context_wrap(satellite_version_rb))
    expected = ('6.1.3', '6.1.3', None, 6, 1)
    result = SatelliteVersion(rpms, sat)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]


def test_get_sat62_version():
    rpms = InstalledRpms(context_wrap(installed_rpms_62))
    expected = ('satellite-6.2.0.11-1.el7sat',
                '6.2.0.11', '1.el7sat', 6, 2)
    result = SatelliteVersion(rpms, None)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.version == expected[1]
    assert result.release == expected[2]


def test_get_sat62_capsule_version():
    rpms = InstalledRpms(context_wrap(installed_rpms_62_cap))
    expected = ('satellite-capsule-6.2.0.11-1.el7sat',
                '6.2.0.11', '1.el7sat', 6, 2)
    result = CapsuleVersion(rpms)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.version == expected[1]
    assert result.release == expected[2]


def test_no_sat_installed():
    rpms = InstalledRpms(context_wrap(no_sat))
    with pytest.raises(SkipComponent) as sc:
        SatelliteVersion(rpms, None)
    assert "Not a Satellite machine" in str(sc)

    rpms = InstalledRpms(context_wrap(installed_rpms_611x_confilct))
    with pytest.raises(SkipComponent) as sc:
        SatelliteVersion(rpms, None)
    assert "unable to determine Satellite version" in str(sc)


def test_doc_examples():
    sat_rpms = InstalledRpms(context_wrap(installed_rpms_62))
    cap_rpms = InstalledRpms(context_wrap(installed_rpms_62_cap))
    env = {
            'sat_ver': SatelliteVersion(sat_rpms, None),
            'cap_ver': CapsuleVersion(cap_rpms),
          }
    failed, total = doctest.testmod(satellite_version, globs=env)
    assert failed == 0
