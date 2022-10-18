import requests

from insights.client.collection_rules import InsightsUploadConf
from insights.client.connection import InsightsConnection
from insights.client.config import InsightsConfig
from mock.mock import patch, Mock
from insights.specs.default import DefaultSpecs
from insights.specs.sos_archive import SosSpecs
from insights.client.map_components import (map_rm_conf_to_components,
                                            _search_uploader_json,
                                            _get_component_by_symbolic_name)

config = InsightsConfig()
conn = InsightsConnection(config)
default_specs = vars(DefaultSpecs).keys()
sos_specs = vars(SosSpecs).keys()


def get_uploader_json():
    '''
    Download latest uploader.json to use for unit tests
    '''
    print("Downloading a fresh and hot uploader.json...")
    url = "https://api.access.redhat.com/r/insights/v1/static/uploader.v2.json"
    uploader_json = requests.get(url).json()
    return uploader_json


uploader_json = get_uploader_json()


@patch('insights.client.collection_rules.InsightsUploadConf.load_redaction_file', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.InsightsUploadConf.get_conf_file', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.map_rm_conf_to_components')
def test_called_when_core_collection_enabled(map_rm_conf_to_components):
    '''
    Verify that the function is called from get_rm_conf when core_collect=True
    '''
    upload_conf = InsightsUploadConf(Mock(core_collect=True))
    upload_conf.get_rm_conf()
    map_rm_conf_to_components.assert_called_once_with({'test': 'test'}, {'test': 'test'})


@patch('insights.client.collection_rules.InsightsUploadConf.load_redaction_file', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.InsightsUploadConf.get_conf_file', Mock(return_value={'test': 'test'}))
@patch('insights.client.collection_rules.map_rm_conf_to_components')
def test_not_called_when_core_collection_disabled(map_rm_conf_to_components):
    '''
    Verify that the function is not called from get_rm_conf when core_collect=False
    '''
    upload_conf = InsightsUploadConf(Mock(core_collect=False))
    upload_conf.get_rm_conf()
    map_rm_conf_to_components.assert_not_called()


def test_search_uploader_json():
    '''
    Verify that all valid input from an uploader.json-based remove.conf
    will return a symbolic name
    '''
    for cmd in uploader_json['commands']:
        assert _search_uploader_json(uploader_json, ['commands'], cmd['command'])
        assert _search_uploader_json(uploader_json, ['commands'], cmd['symbolic_name'])
    for fil in uploader_json['files']:
        assert _search_uploader_json(uploader_json, ['files', 'globs'], fil['file'])
        assert _search_uploader_json(uploader_json, ['files', 'globs'], fil['symbolic_name'])
    for glb in uploader_json['globs']:
        assert _search_uploader_json(uploader_json, ['files', 'globs'], glb['symbolic_name'])


def test_search_uploader_json_invalid():
    '''
    Verify that invalid input will return None
    '''
    assert _search_uploader_json(uploader_json, ['commands'], 'random value') is None
    assert _search_uploader_json(uploader_json, ['files', 'globs'], 'random value') is None


def test_search_uploader_json_globs_symbolic_only():
    '''
    Verify that globs are matched by symbolic name only
    '''
    for glb in uploader_json['globs']:
        assert _search_uploader_json(uploader_json, ['files', 'globs'], glb['glob']) is None


def test_map_rm_conf_to_components_sym_names():
    '''
    Verify that all symbolic names in uploader.json result as
    components in the output
    '''
    # commands
    for cmd in uploader_json['commands']:
        # run each possible command through the function
        sym_name = cmd['symbolic_name']
        rm_conf = {'commands': [sym_name]}
        # figure out the destination name should be
        spec_name = _get_component_by_symbolic_name(sym_name)
        new_rm_conf = map_rm_conf_to_components(rm_conf, uploader_json)
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
        new_rm_conf = map_rm_conf_to_components(rm_conf, uploader_json)
        # files should be empty, components should have 1 item
        # except for these which cannot be mapped to specs.
        # in which case, components empty and these remain in files
        if sym_name == 'redhat_access_proactive_log':
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
        new_rm_conf = map_rm_conf_to_components(rm_conf, uploader_json)
        # files should be empty, components should have 1 item
        assert len(new_rm_conf['files']) == 0
        assert len(new_rm_conf['components']) == 1
        assert new_rm_conf['components'][0] == spec_name


def test_map_rm_conf_to_components_raw_cmds_files():
    '''
    Verify that all raw files/commands in uploader.json result as
    components in the output
    '''
    # commands
    for cmd in uploader_json['commands']:
        # run each possible command through the function
        rm_conf = {'commands': [cmd['command']]}
        sym_name = cmd['symbolic_name']
        # figure out the destination name should be
        spec_name = _get_component_by_symbolic_name(sym_name)
        new_rm_conf = map_rm_conf_to_components(rm_conf, uploader_json)
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
        new_rm_conf = map_rm_conf_to_components(rm_conf, uploader_json)
        # files should be empty, components should have 1 item
        # except for these which cannot be mapped to specs.
        # in which case, components empty and these remain in files
        if fil['file'] == '/var/log/redhat_access_proactive/redhat_access_proactive.log':
            assert len(new_rm_conf['files']) == 1
            assert new_rm_conf['files'][0] == fil['file']
            assert len(new_rm_conf['components']) == 0
        else:
            assert len(new_rm_conf['files']) == 0
            assert len(new_rm_conf['components']) == 1
            assert new_rm_conf['components'][0] == spec_name


def test_map_rm_conf_to_components_invalid():
    '''
    Verify that matching commands/files are mapped to components
    '''
    rm_conf = {'commands': ['random', 'value'], 'files': ['other', 'invalid', 'data']}
    new_rm_conf = map_rm_conf_to_components(rm_conf, uploader_json)
    # rm_conf should be unchanged
    assert len(new_rm_conf['commands']) == 2
    assert len(new_rm_conf['files']) == 3
    assert len(new_rm_conf['components']) == 0
    assert new_rm_conf['commands'] == rm_conf['commands']
    assert new_rm_conf['files'] == rm_conf['files']


@patch('insights.client.map_components._search_uploader_json')
def test_rm_conf_empty(_search_uploader_json):
    '''
    Verify the function returns rm_conf unchanged if called
    with an empty dict or None
    '''
    rm_conf = {}
    new_rm_conf = map_rm_conf_to_components(rm_conf, uploader_json)
    _search_uploader_json.assert_not_called()
    assert new_rm_conf == {}

    rm_conf = None
    new_rm_conf = map_rm_conf_to_components(rm_conf, uploader_json)
    _search_uploader_json.assert_not_called()
    assert new_rm_conf is None


@patch('insights.client.map_components.logger.warning')
def test_log_long_key(logger_warning):
    '''
    Verify the conversion table is logged with proper
    spacing, wrapping, and unconverted specs are not logged
    '''
    rm_conf = {'commands': ["/usr/bin/find /etc/origin/node /etc/origin/master /etc/pki /etc/ipa /etc/tower/tower.cert -type f -exec /usr/bin/openssl x509 -noout -enddate -in '{}' \\; -exec echo 'FileName= {}' \\;",
                            "/usr/bin/md5sum /etc/pki/product/69.pem"],
               'files': ["/etc/sysconfig/virt-who",
                         "/etc/yum.repos.d/fedora-cisco-openh264.repo",
                         "krb5_conf_d"]}
    map_rm_conf_to_components(rm_conf, uploader_json)
    logger_warning.assert_any_call("- /usr/bin/find /etc/origin/node                   => certificates_enddate\n  /etc/origin/master /etc/pki /etc/ipa\n  /etc/tower/tower.cert -type f -exec\n  /usr/bin/openssl x509 -noout -enddate -in '{}'\n  \\; -exec echo 'FileName= {}' \\;")
    logger_warning.assert_any_call("- /usr/bin/md5sum /etc/pki/product/69.pem          => md5chk_files")
    logger_warning.assert_any_call("- krb5_conf_d                                      => krb5")


@patch('insights.client.map_components.logger.warning')
def test_log_short_key(logger_warning):
    '''
    Verify the conversion table is logged without wrapping or spacing when key
    is short
    '''
    rm_conf = {'commands': ["ss_tupna"]}
    map_rm_conf_to_components(rm_conf, uploader_json)
    logger_warning.assert_any_call("If possible, commands and files specified in the blacklist configuration will be converted to Insights component specs that will be disabled as needed.")


def test_components_added():
    '''
    Verify that the resulting component list is
    an aggregation of the current list and the conversion results
    with no duplicates.
    '''
    rm_conf = {'commands': ["/usr/bin/md5sum /etc/pki/product/69.pem"],
               'components': ["insights.specs.default.DefaultSpecs.sysconfig_virt_who"]}
    results = map_rm_conf_to_components(rm_conf, uploader_json)

    assert results == {'commands': [],
                       'files': [],
                       'components': ["insights.specs.default.DefaultSpecs.sysconfig_virt_who",
                                      "insights.specs.default.DefaultSpecs.md5chk_files"]}
