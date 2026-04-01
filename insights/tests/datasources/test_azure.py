import json
import pytest

from collections import defaultdict
from unittest.mock import Mock

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs
from insights.specs.datasources.azure import LocalSpecs, azure_instance_compute_metadata

AZURE_INSTANCE_COMPUTE_METADATA = """
{"licenseType": "", "offer": "RHEL", "plan": {"name": "", "product": "", "publisher": ""}, "tagsList": [], "vmId": "3c29e210-0669-496f-812a-2fffffffffff", "vmSize": "Standard_B1s"}
""".strip()

AZURE_INSTANCE_COMPUTE_METADATA_AB_CURL = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()

AZURE_INSTANCE_COMPUTE_METADATA_AB_JSON = """
"some string"
""".strip()

AZURE_INSTANCE_COMPUTE_METADATA_AB_UNPARSABLE = """
"keyA": "", "KeyB": "RHEL"}
""".strip()

AZURE_INSTANCE_COMPUTE_METADATA_MISMATCH = """
{"keyA": "", "KeyB": "RHEL"}
""".strip()

AZURE_INSTANCE_COMPUTE_METADATA_FILTERED_JSON = {
    "licenseType": "",
    "offer": "RHEL",
    "plan": {"name": "", "product": "", "publisher": ""},
    "vmId": "3c29e210-0669-496f-812a-2fffffffffff",
    "vmSize": "Standard_B1s",
}

RELATIVE_PATH = 'insights_datasources/azure_instance_compute_metadata'


def setup_function(func):
    if (
        func is test_azure_instance_compute_metadata_datasource
        or func is test_azure_instance_compute_metadata_datasource_abnormal_output
    ):
        filters.add_filter(
            Specs.azure_instance_compute_metadata,
            ["vmSize", "vmId", "plan", "offer", "licenseType", "someRandomKey"],
        )
    if func is test_azure_instance_compute_metadata_datasource_no_filter:
        filters.add_filter(Specs.azure_instance_compute_metadata, [])


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_azure_instance_compute_metadata_datasource():
    azure_instance_compute_metadata_data = Mock()
    azure_instance_compute_metadata_data.content = AZURE_INSTANCE_COMPUTE_METADATA.splitlines()
    broker = {LocalSpecs.azure_instance_compute_metadata_raw: azure_instance_compute_metadata_data}
    result = azure_instance_compute_metadata(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(
        content=json.dumps(AZURE_INSTANCE_COMPUTE_METADATA_FILTERED_JSON, sort_keys=True),
        relative_path=RELATIVE_PATH,
    )
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_azure_instance_compute_metadata_datasource_no_filter():
    azure_instance_compute_metadata_data = Mock()
    azure_instance_compute_metadata_data.content = AZURE_INSTANCE_COMPUTE_METADATA.splitlines()
    broker = {LocalSpecs.azure_instance_compute_metadata_raw: azure_instance_compute_metadata_data}
    with pytest.raises(SkipComponent) as e:
        azure_instance_compute_metadata(broker)
    assert 'No filters defined' in str(e)


def test_azure_instance_compute_metadata_datasource_abnormal_output():
    azure_instance_compute_metadata_data = Mock()
    azure_instance_compute_metadata_data.content = (
        AZURE_INSTANCE_COMPUTE_METADATA_AB_CURL.splitlines()
    )
    broker = {LocalSpecs.azure_instance_compute_metadata_raw: azure_instance_compute_metadata_data}
    with pytest.raises(SkipComponent) as e:
        azure_instance_compute_metadata(broker)
    assert 'Empty content or curl error' in str(e)

    azure_instance_compute_metadata_data = Mock()
    azure_instance_compute_metadata_data.content = (
        AZURE_INSTANCE_COMPUTE_METADATA_AB_JSON.splitlines()
    )
    broker = {LocalSpecs.azure_instance_compute_metadata_raw: azure_instance_compute_metadata_data}
    with pytest.raises(SkipComponent) as e:
        azure_instance_compute_metadata(broker)
    assert 'Invalid JSON format' in str(e)

    azure_instance_compute_metadata_data = Mock()
    azure_instance_compute_metadata_data.content = (
        AZURE_INSTANCE_COMPUTE_METADATA_MISMATCH.splitlines()
    )
    broker = {LocalSpecs.azure_instance_compute_metadata_raw: azure_instance_compute_metadata_data}
    with pytest.raises(SkipComponent) as e:
        azure_instance_compute_metadata(broker)
    assert 'No matching filters found in metadata' in str(e)

    azure_instance_compute_metadata_data = Mock()
    azure_instance_compute_metadata_data.content = (
        AZURE_INSTANCE_COMPUTE_METADATA_AB_UNPARSABLE.splitlines()
    )
    broker = {LocalSpecs.azure_instance_compute_metadata_raw: azure_instance_compute_metadata_data}
    with pytest.raises(SkipComponent) as e:
        azure_instance_compute_metadata(broker)
    assert 'Failed to parse metadata' in str(e)
