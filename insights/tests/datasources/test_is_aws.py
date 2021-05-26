import pytest
from insights.combiners.cloud_provider import CloudProvider
from insights.combiners.tests.test_cloud_provider import RPMS, RPMS_AWS, DMIDECODE, DMIDECODE_AWS
from insights.parsers import SkipComponent
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.dmidecode import DMIDecode
from insights.specs.datasources import is_aws
from insights.tests import context_wrap


def test_is_aws():
    rpms = InstalledRpms(context_wrap(RPMS_AWS))
    dmidecode = DMIDecode(context_wrap(DMIDECODE_AWS))
    cp = CloudProvider(rpms, dmidecode, None, None)
    broker = {CloudProvider: cp}
    assert is_aws(broker)


def test_not_is_aws():
    rpms = InstalledRpms(context_wrap(RPMS))
    dmidecode = DMIDecode(context_wrap(DMIDECODE))
    cp = CloudProvider(rpms, dmidecode, None, None)
    broker = {CloudProvider: cp}
    with pytest.raises(SkipComponent):
        is_aws(broker)
