from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.satellite_version import Satellite6Version
from insights.combiners.satellite_version import satellite_version
from insights.tests import context_wrap


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

installed_rpms_61 = """
foreman-1.7.2.53-1.el7sat.noarch                            Wed May 18 14:16:25 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el6.x86_64                                     Wed May 18 14:16:25 2016
"""

installed_rpms_62 = """
foreman-1.11.0.53-1.el7sat.noarch                           Wed May 18 14:16:25 2016
scl-utils-20120927-27.el7_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el7.x86_64                                     Wed May 18 14:16:25 2016
satellite-6.2.0.11-1.el7sat.noarch                Wed May 18 14:16:25 2016
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


def test_get_sat5_version():
    rpms = InstalledRpms(context_wrap(installed_rpms_5))
    shared = {InstalledRpms: rpms}
    expected = ('satellite-schema-5.6.0.10-1.el6sat',
                '5.6.0.10', '1.el6sat', 5, 6)
    result = satellite_version(shared)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]


def test_get_sat61_version():
    rpms = InstalledRpms(context_wrap(installed_rpms_61))
    shared = {InstalledRpms: rpms}
    expected = ('6.1.7', '6.1.7', None, 6, 1)
    result = satellite_version(shared)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]

    sat = Satellite6Version(context_wrap(satellite_version_rb))
    shared = {Satellite6Version: sat}
    expected = ('6.1.3', '6.1.3', None, 6, 1)
    result = satellite_version(shared)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]


def test_get_sat61_version_both():
    rpms = InstalledRpms(context_wrap(installed_rpms_61))
    sat = Satellite6Version(context_wrap(satellite_version_rb))
    shared = {InstalledRpms: rpms, Satellite6Version: sat}
    expected = ('6.1.3', '6.1.3', None, 6, 1)
    result = satellite_version(shared)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.release == expected[2]
    assert result.version == expected[1]


def test_get_sat62_version():
    rpms = InstalledRpms(context_wrap(installed_rpms_62))
    shared = {InstalledRpms: rpms}
    expected = ('satellite-6.2.0.11-1.el7sat',
                '6.2.0.11', '1.el7sat', 6, 2)
    result = satellite_version(shared)
    assert result.major == expected[-2]
    assert result.minor == expected[-1]
    assert result.full == expected[0]
    assert result.version == expected[1]
    assert result.release == expected[2]


def test_no_sat_installed():
    rpms = InstalledRpms(context_wrap(no_sat))
    sat = Satellite6Version(context_wrap(installed_rpms_61))
    shared = {InstalledRpms: rpms, Satellite6Version: sat}
    result = satellite_version(shared)
    assert result is None
