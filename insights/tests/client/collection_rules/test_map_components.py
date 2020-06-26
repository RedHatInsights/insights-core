import pkgutil
import insights
import json

from insights.client.config import InsightsConfig
from insights.client.collection_rules import InsightsUploadConf
from mock.mock import patch, Mock, call
from insights.specs.default import DefaultSpecs
from insights.specs.sos_archive import SosSpecs
from insights.client.map_components import map_rm_conf_to_components, _get_component_by_symbolic_name


# @patch('insights.client.collection_rules.InsightsUploadConf.load_redaction_file', Mock(return_value={'test': 'test'}))
# @patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old', Mock(return_value={'test': 'test'}))
# @patch('insights.client.collection_rules.map_rm_conf_to_components')
# def test_called_when_core_collection_enabled(map_rm_conf_to_components):
#     '''
#     Verify that the function is called from get_rm_conf when core_collect=True
#     '''
#     upload_conf = InsightsUploadConf(Mock(core_collect=True))
#     upload_conf.get_rm_conf()
#     map_rm_conf_to_components.assert_called_once_with({'test': 'test'})


# @patch('insights.client.collection_rules.InsightsUploadConf.load_redaction_file', Mock(return_value={'test': 'test'}))
# @patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old', Mock(return_value={'test': 'test'}))
# @patch('insights.client.collection_rules.map_rm_conf_to_components')
# def test_not_called_when_core_collection_disabled(map_rm_conf_to_components):
#     '''
#     Verify that the function is not called from get_rm_conf when core_collect=False
#     '''
#     upload_conf = InsightsUploadConf(Mock(core_collect=False))
#     upload_conf.get_rm_conf()
#     map_rm_conf_to_components.assert_not_called()


def test_all_sym_names_match_components():
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


def test_all_sym_names_can_be_mapped():
    '''
    Verify that all symbolic names in uploader.json result as
    components in the output
    '''
    uploader_json_file = pkgutil.get_data(insights.__name__, "uploader_json_map.json")
    uploader_json = json.loads(uploader_json_file)

    # commands
    for cmd in uploader_json['commands']:
        # run each possible command through the function
        sym_name = cmd['symbolic_name']
        rm_conf = {'commands': [sym_name]}
        # figure out the destination name should be
        spec_name = _get_component_by_symbolic_name(sym_name)
        new_rm_conf = map_rm_conf_to_components(rm_conf)
        # commands should be empty, components should have 1 item
        assert len(new_rm_conf['commands']) == 0
        assert len(new_rm_conf['components']) == 1
        assert new_rm_conf['components'][0] == spec_name

    # files
    for fil in uploader_json['files']:
        # run each possible file through the function
        sym_name = fil['symbolic_name']
        rm_conf = {'files': [sym_name]}
        # figure out the destination name should be
        spec_name = _get_component_by_symbolic_name(sym_name)
        new_rm_conf = map_rm_conf_to_components(rm_conf)
        # files should be empty, components should have 1 item
        # except for these which cannot be mapped to specs.
        # in which case, components empty and these remain in files
        if sym_name in ['grub2_efi_grubenv',
                        'grub2_grubenv',
                        'redhat_access_proactive_log']:
            assert len(new_rm_conf['files']) == 1
            assert new_rm_conf['files'][0] == sym_name
            assert len(new_rm_conf['components']) == 0
        else:
            assert len(new_rm_conf['files']) == 0
            assert len(new_rm_conf['components']) == 1
            assert new_rm_conf['components'][0] == spec_name

    # globs
    for glb in uploader_json['globs']:
        # run each possible glob through the function
        sym_name = glb['symbolic_name']
        rm_conf = {'files': [sym_name]}
        # figure out the destination name should be
        spec_name = _get_component_by_symbolic_name(sym_name)
        new_rm_conf = map_rm_conf_to_components(rm_conf)
        # files should be empty, components should have 1 item
        assert len(new_rm_conf['files']) == 0
        assert len(new_rm_conf['components']) == 1
        assert new_rm_conf['components'][0] == spec_name


def test_all_raw_cmds_files_can_be_mapped():
    '''
    Verify that all raw files/commands in uploader.json result as
    components in the output
    '''
    uploader_json_file = pkgutil.get_data(insights.__name__, "uploader_json_map.json")
    uploader_json = json.loads(uploader_json_file)

    # commands
    for cmd in uploader_json['commands']:
        # run each possible command through the function
        rm_conf = {'commands': [cmd['command']]}
        sym_name = cmd['symbolic_name']
        # figure out the destination name should be
        spec_name = _get_component_by_symbolic_name(sym_name)
        new_rm_conf = map_rm_conf_to_components(rm_conf)
        # commands should be empty, components should have 1 item
        assert len(new_rm_conf['commands']) == 0
        assert len(new_rm_conf['components']) == 1
        assert new_rm_conf['components'][0] == spec_name

    # files
    for fil in uploader_json['files']:
        # run each possible file through the function
        rm_conf = {'files': [fil['file']]}
        sym_name = fil['symbolic_name']
        # figure out the destination name should be
        spec_name = _get_component_by_symbolic_name(sym_name)
        new_rm_conf = map_rm_conf_to_components(rm_conf)
        # files should be empty, components should have 1 item
        # except for these which cannot be mapped to specs.
        # in which case, components empty and these remain in files
        if fil['file'] in ['/boot/efi/EFI/redhat/grubenv',
                           '/boot/grub2/grubenv',
                           '/var/log/redhat_access_proactive/redhat_access_proactive.log']:
            assert len(new_rm_conf['files']) == 1
            assert new_rm_conf['files'][0] == fil['file']
            assert len(new_rm_conf['components']) == 0
        else:
            assert len(new_rm_conf['files']) == 0
            assert len(new_rm_conf['components']) == 1
            assert new_rm_conf['components'][0] == spec_name


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