import pytest

from insights import SkipComponent
from insights.components.insights_core import CoreEgg, CoreRpm
from insights.parsers.installed_rpms import InstalledRpms
from insights.tests import context_wrap


RPMS_CLIENT_CORE = """
{"name":"insights-core","epoch":"(none)","version":"3.7.2.2","release":"2.el9","arch":"x86_64","installtime":"Mon Mar 26 16:32:08 2018","buildtime":"1457608025","vendor":"Red Hat, Inc.","buildhost":"x86-024.build.eng.bos.redhat.com","sigpgp":"RSA/SHA256, Fri Mar 18 05:15:10 2016, Key ID 199e2f91fd431d51"}
{"name":"insights-client","epoch":"(none)","version":"3.9.3","release":"1.el9","arch":"x86_64","installtime":"Mon Mar 26 16:32:08 2018","buildtime":"1457608025","vendor":"Red Hat, Inc.","buildhost":"x86-024.build.eng.bos.redhat.com","sigpgp":"RSA/SHA256, Fri Mar 18 05:15:10 2016, Key ID 199e2f91fd431d51"}
"""

RPMS_NO_CLIENT_CORE = """
{"name":"insights-core","epoch":"(none)","version":"3.7.2.2","release":"2.el9","arch":"x86_64","installtime":"Mon Mar 26 16:32:08 2018","buildtime":"1457608025","vendor":"Red Hat, Inc.","buildhost":"x86-024.build.eng.bos.redhat.com","sigpgp":"RSA/SHA256, Fri Mar 18 05:15:10 2016, Key ID 199e2f91fd431d51"}
"""

RPMS_CLIENT_NO_CORE = """
{"name":"insights-client","epoch":"(none)","version":"3.9.3","release":"1.el9","arch":"x86_64","installtime":"Mon Mar 26 16:32:08 2018","buildtime":"1457608025","vendor":"Red Hat, Inc.","buildhost":"x86-024.build.eng.bos.redhat.com","sigpgp":"RSA/SHA256, Fri Mar 18 05:15:10 2016, Key ID 199e2f91fd431d51"}
"""

RPMS_OLD_CLIENT_CORE = """
{"name":"insights-core","epoch":"(none)","version":"3.7.2.2","release":"2.el9_2","arch":"x86_64","installtime":"Mon Mar 26 16:32:08 2018","buildtime":"1457608025","vendor":"Red Hat, Inc.","buildhost":"x86-024.build.eng.bos.redhat.com","sigpgp":"RSA/SHA256, Fri Mar 18 05:15:10 2016, Key ID 199e2f91fd431d51"}
{"name":"insights-client","epoch":"(none)","version":"3.9.0","release":"1.el9","arch":"x86_64","installtime":"Mon Mar 26 16:32:08 2018","buildtime":"1457608025","vendor":"Red Hat, Inc.","buildhost":"x86-024.build.eng.bos.redhat.com","sigpgp":"RSA/SHA256, Fri Mar 18 05:15:10 2016, Key ID 199e2f91fd431d51"}
"""


def test_core_egg():
    rpms = InstalledRpms(context_wrap(RPMS_CLIENT_NO_CORE))
    egg = CoreEgg(rpms)
    assert egg is not None
    with pytest.raises(SkipComponent):
        CoreRpm(rpms)

    rpms = InstalledRpms(context_wrap(RPMS_OLD_CLIENT_CORE))
    egg = CoreEgg(rpms)
    assert egg is not None
    with pytest.raises(SkipComponent):
        CoreRpm(rpms)


def test_core_rpm():
    rpms = InstalledRpms(context_wrap(RPMS_CLIENT_CORE))
    with pytest.raises(SkipComponent):
        CoreEgg(rpms)
    rpm = CoreRpm(rpms)
    assert rpm is not None


def test_core_unknown():
    # It will never happen
    rpms = InstalledRpms(context_wrap(RPMS_NO_CLIENT_CORE))
    with pytest.raises(SkipComponent):
        CoreRpm(rpms)
    with pytest.raises(SkipComponent):
        CoreEgg(rpms)
