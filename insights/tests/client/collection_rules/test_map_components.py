import pkgutil
import insights
import json

from insights.client.config import InsightsConfig
from insights.client.collection_rules import InsightsUploadConf
from mock.mock import patch, Mock, call
from insights.specs.default import DefaultSpecs
from insights.specs.sos_archive import SosSpecs
from insights.client.map_components import map_rm_conf_to_components, _get_component_by_symbolic_name


@patch('insights.client.collection_rules.InsightsUploadConf.load_redaction_file', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.map_rm_conf_to_components')
def test_called_when_core_collection_enabled(map_rm_conf_to_components):
    '''
    Verify that the function is called from get_rm_conf when core_collect=True
    '''
    upload_conf = InsightsUploadConf(Mock(core_collect=True))
    upload_conf.get_rm_conf()
    map_rm_conf_to_components.assert_called_once_with({'test': 'test'})


@patch('insights.client.collection_rules.InsightsUploadConf.load_redaction_file', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.map_rm_conf_to_components')
def test_not_called_when_core_collection_disabled(map_rm_conf_to_components):
    '''
    Verify that the function is not called from get_rm_conf when core_collect=False
    '''
    upload_conf = InsightsUploadConf(Mock(core_collect=False))
    upload_conf.get_rm_conf()
    map_rm_conf_to_components.assert_not_called()


def test_all_specs_mapped_to_real_components():
    '''
    Verify that all symbolic names in uploader.json can be mapped
    to valid components as prescribed in the conversion function
    '''
    uploader_json_file = pkgutil.get_data(insights.__name__, "uploader_json_map.json")
    uploader_json = json.loads(uploader_json_file)
    default_specs = vars(DefaultSpecs).keys()
    sos_specs = vars(SosSpecs).keys()

    for category in ['commands', 'files', 'globs']:
        for entry in uploader_json[category]:
            full_component = _get_component_by_symbolic_name(entry['symbolic_name'])

            if full_component is None:
                # this entry should not be in core, so assert that it's missing
                assert entry['symbolic_name'] not in default_specs
                continue

            module, shortname = full_component.rsplit('.', 1)

            if module == "insights.specs.default.DefaultSpecs":
                assert shortname in default_specs
            elif module == "insights.specs.sos_archive.SosSpecs":
                assert shortname in sos_specs
            else:
                # invalid module name
                assert False


def test_map_rm_conf_to_components_mapped():
    '''
    Verify that matching commands/files are mapped to components
    '''
    input_commands = []
    input_files = []
    expected_components = []


def test_map_rm_conf_to_components_mismatch():
    '''
    Verify that commands/files not matching components are
    left in their respective lists
    '''
    input_commands = []
    input_files = []
    expected_components = []


def test_map_rm_conf_to_components_glob_symbolic_name_only():
    '''
    Verify that globs are matched by symbolic name only
    '''
    input_commands = []
    input_files = []
    expected_components = []