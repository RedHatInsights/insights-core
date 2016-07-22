from falafel.tests import context_wrap
from falafel.mappers.satellite_version import get_sat_version

installed_rpms = """
satellite-branding-5.5.0.22-1.el6sat.noarch                 Wed May 18 14:50:17 2016
satellite-doc-indexes-5.6.0-2.el6sat.noarch                 Wed May 18 14:47:49 2016
satellite-repo-5.6.0.3-1.el6sat.noarch                      Wed May 18 14:37:34 2016
satellite-schema-5.6.0.10-1.el6sat.noarch                   Wed May 18 14:53:03 2016
satyr-0.16-2.el6.x86_64                                     Wed May 18 14:16:08 2016
scdb-1.15.8-1.el6sat.noarch                                 Wed May 18 14:48:14 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el6.x86_64                                     Wed May 18 14:16:25 2016
"""

satellite_version = """
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
    result = get_sat_version(context_wrap(installed_rpms))
    assert result == "5.6.0.10-1.el6sat.noarch"


def test_get_sat6_version():
    result = get_sat_version(context_wrap(satellite_version))
    assert result == "6.1.3"


def test_get_sat_version():
    result = get_sat_version(context_wrap(no_sat))
    assert result is None
