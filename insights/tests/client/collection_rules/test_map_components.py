from mock.mock import patch, Mock

from insights.client.collection_rules import InsightsUploadConf
from insights.client.map_components import map_rm_conf_to_components, _search_specs


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
    map_rm_conf_to_components.assert_called_once_with({'test': 'test'})


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


def test_search_specs():
    '''
    Verify that all valid input from remove.conf will return a symbolic name
    '''
    mappings = {
        # symbolic_name
        'os_release': ['os_release'],
        # commands
        '/usr/bin/uname -a': ['uname'],
        '/bin/date --utc': ['date_utc'],
        # foreach_execute
        '/sbin/ethtool %s': ['ethtool'],
        # command_with_args
        '/usr/bin/getent group %s': ['group_info'],
        # files
        '/var/log/dmesg': ['dmesg_log'],
        '/var/log/yum.log': ['yum_log'],
        # globs
        '/etc/yum.repos.d/*.repo': ['yum_repos_d'],
        # foreach_collect
        '/proc/%s/limits': ['httpd_limits'],
        # first_of
        '/usr/bin/lsof': ['lsof'],
        '/usr/sbin/lsof': ['lsof'],
        # container_collect
        '/etc/redhat-release': ['redhat_release', 'container_redhat_release'],
        # container_execute
        '/bin/ps aux': ['ps_aux', 'container_ps_aux']
    }
    for pat, specs in mappings.items():
        ret = _search_specs(pat)
        for spec in specs:
            spec_name = "insights.specs.default.DefaultSpecs.{0}".format(spec)
            assert spec_name in ret


def test_search_specs_invalid():
    '''
    Verify that invalid input will return None
    '''
    assert len(_search_specs('random value')) == 0


def test_map_rm_conf_to_components_invalid():
    '''
    Verify that matching commands/files are mapped to components
    '''
    rm_conf = {'commands': ['random', 'value'], 'files': ['other', 'invalid', 'data']}
    new_rm_conf = map_rm_conf_to_components(rm_conf)
    # rm_conf should be unchanged
    assert len(new_rm_conf['commands']) == 2
    assert len(new_rm_conf['files']) == 3
    assert len(new_rm_conf['components']) == 0
    assert new_rm_conf['commands'] == rm_conf['commands']
    assert new_rm_conf['files'] == rm_conf['files']


@patch('insights.client.map_components._search_specs')
def test_rm_conf_empty(_search_specs):
    '''
    Verify the function returns rm_conf unchanged if called
    with an empty dict or None
    '''
    rm_conf = {}
    new_rm_conf = map_rm_conf_to_components(rm_conf)
    _search_specs.assert_not_called()
    assert new_rm_conf == {}

    rm_conf = None
    new_rm_conf = map_rm_conf_to_components(rm_conf)
    _search_specs.assert_not_called()
    assert new_rm_conf is None


@patch('insights.client.map_components.logger.warning')
def test_log_long_key(logger_warning):
    '''
    Verify the conversion table is logged with proper
    spacing, wrapping, and unconverted specs are not logged
    '''
    rm_conf = {'commands': ["/usr/bin/find /etc/origin/node /etc/origin/master /etc/pki /etc/ipa /etc/tower/tower.cert -type f -exec /usr/bin/openssl x509 -noout -enddate -in '{}' \\; -exec echo 'FileName= {}' \\;",
                            "/usr/bin/md5sum %s"],
               'files': ["/etc/sysconfig/virt-who",
                         "/etc/yum.repos.d/fedora-cisco-openh264.repo",
                         "krb5"]}
    map_rm_conf_to_components(rm_conf)
    logger_warning.assert_any_call("- /usr/bin/find /etc/origin/node                   => certificates_enddate\n  /etc/origin/master /etc/pki /etc/ipa\n  /etc/tower/tower.cert -type f -exec\n  /usr/bin/openssl x509 -noout -enddate -in '{}'\n  \\; -exec echo 'FileName= {}' \\;")
    logger_warning.assert_any_call("- /usr/bin/md5sum %s                               => md5chk_files")
    logger_warning.assert_any_call("- krb5                                             => krb5")


@patch('insights.client.map_components.logger.warning')
def test_log_short_key(logger_warning):
    '''
    Verify the conversion table is logged without wrapping or spacing when key
    is short
    '''
    rm_conf = {'commands': ["ss_tupna"]}
    map_rm_conf_to_components(rm_conf)
    logger_warning.assert_any_call("If possible, commands and files specified in the blacklist configuration will be converted to Insights component specs that will be disabled as needed.")


def test_components_added():
    '''
    Verify that the resulting component list is
    an aggregation of the current list and the conversion results
    with no duplicates.
    '''
    rm_conf = {'commands': ["/usr/bin/md5sum %s"],
               'components': ["insights.specs.default.DefaultSpecs.sysconfig_virt_who"]}
    results = map_rm_conf_to_components(rm_conf)

    assert results == {'commands': [],
                       'files': [],
                       'components': ["insights.specs.default.DefaultSpecs.sysconfig_virt_who",
                                      "insights.specs.default.DefaultSpecs.md5chk_files"]}
