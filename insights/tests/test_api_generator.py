import pytest

from insights.tools import generate_api_config
from insights.parsers import *  # noqa


@pytest.fixture
def latest():
    return generate_api_config.APIConfigGenerator().serialize_data_spec()


def test_top_level(latest):
    # these sections must exist and not be empty
    for each in ['version', 'files', 'commands', 'specs', 'pre_commands', 'meta_specs']:
        assert each in latest
        assert len(latest[each]) > 0


def test_meta_specs(latest):
    # these sections must exist in the meta_specs, have a 'archive_file_name' field,
    # and it must not be empty
    for each in ['analysis_target', 'branch_info', 'machine-id', 'uploader_log']:
        assert each in latest['meta_specs']
        assert 'archive_file_name' in latest['meta_specs'][each]
        assert len(latest['meta_specs'][each]['archive_file_name']) > 0


def test_specs(latest):
    # check that each spec only has target sections for known targets
    for eachspec in latest['specs']:
        for eachtarget in latest['specs'][eachspec]:
            assert eachtarget in ['host', 'docker_container', 'docker_image']
