from insights.tests import context_wrap
from insights.parsers.dmidecode import DMIDecode
from insights.combiners.cloud_provider import CloudProvider
from insights.components.cloud_provider import IsAWS, IsAzure, IsGCP
from insights.tests.combiners.test_cloud_provider import (
        DMIDECODE_AWS, DMIDECODE_GOOGLE, DMIDECODE_AZURE_ASSET_TAG)


def test_is_aws():
    dmi = DMIDecode(context_wrap(DMIDECODE_AWS))
    cp = CloudProvider(None, dmi, None, None)
    result = IsAWS(cp)
    assert isinstance(result, IsAWS)


def test_is_azure():
    dmi = DMIDecode(context_wrap(DMIDECODE_AZURE_ASSET_TAG))
    cp = CloudProvider(None, dmi, None, None)
    result = IsAzure(cp)
    assert isinstance(result, IsAzure)


def test_is_gcp():
    dmi = DMIDecode(context_wrap(DMIDECODE_GOOGLE))
    cp = CloudProvider(None, dmi, None, None)
    result = IsGCP(cp)
    assert isinstance(result, IsGCP)
