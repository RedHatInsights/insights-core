import pkgutil
import insights
import json

# from insights.client.config import InsightsConfig
from insights.client.collection_rules import InsightsUploadConf
from mock.mock import patch, Mock
from insights.specs.default import DefaultSpecs
from insights.specs.sos_archive import SosSpecs
from insights.client.map_components import (map_rm_conf_to_components,
                                            _search_uploader_json,
                                            _get_component_by_symbolic_name)

uploader_json_file = pkgutil.get_data(insights.__name__, "uploader_json_map.json")
uploader_json = json.loads(uploader_json_file)
default_specs = vars(DefaultSpecs).keys()
sos_specs = vars(SosSpecs).keys()


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


def test_get_component_by_symbolic_name():
    '''
    Verify that all symbolic names in uploader.json can be mapped
    to valid components as prescribed in the conversion function
    '''
    # some specs have been removed for core release so because they either
    #   A) do not appear in uploader.json, or
    #   B) DO appear in uploader.json, but have no associated rules
    #   Filter out the (B) specs with this list
    skipped_specs = [
        'ceph_osd_df',
        'dmsetup_info',
        'du_dirs',
        'gluster_peer_status',
        'gluster_v_status',
        'heat_crontab',
        'httpd_on_nfs',
        'ls_edac_mc',
        'ls_usr_sbin',
        'lvmconfig',
        'saphostexec_status',
        'saphostexec_version',
        'nova_migration_uid',
        'ntpq_pn',
        'rabbitmq_queues',
        'rhev_data_center',
        'root_crontab',
        'subscription_manager_installed_product_ids',
        'yum_list_installed',
        'zdump_v',
        'cni_podman_bridge_conf',
        'cpu_smt_control',
        'cpu_vulns_meltdown',
        'cpu_vulns_spectre_v1',
        'cpu_vulns_spectre_v2',
        'cpu_vulns_spec_store_bypass',
        'dnf_modules',
        'docker_storage',
        'freeipa_healthcheck_log',
        'vmware_tools_conf',
        'ironic_conf',
        'octavia_conf',
        'partitions',
        'rhn_hibernate_conf',
        'rhn_search_daemon_log',
        'rhosp_release',
        'secure',
        'foreman_tasks_config',
        'ssh_foreman_config',
        'swift_conf',
        'sys_kernel_sched_features',
        'sysconfig_memcached',
        'sysconfig_mongod',
        'systemd_system_origin_accounting',
        'tuned_conf',
        'vdsm_conf',
        'vdsm_id',
        'neutron_ml2_conf',
        'sap_host_profile',
        'sched_rt_runtime_us',
        'libvirtd_qemu_log',
        'mlx4_port'
    ]

    # first, make sure our list is proper and one of these
    #   are in the default specs
    for s in skipped_specs:
        assert s not in default_specs

    for category in ['commands', 'files', 'globs']:
        for entry in uploader_json[category]:
            full_component = _get_component_by_symbolic_name(entry['symbolic_name'])

            if full_component is None:
                # this entry should not be in core, so assert that it's missing
                assert entry['symbolic_name'] not in default_specs
                continue

            module, shortname = full_component.rsplit('.', 1)

            # filter out specs without associated rules
            if shortname in skipped_specs:
                continue

            if module == "insights.specs.default.DefaultSpecs":
                assert shortname in default_specs
            elif module == "insights.specs.sos_archive.SosSpecs":
                assert shortname in sos_specs
            else:
                # invalid module name
                assert False


def test_search_uploader_json():
    '''
    Verify that all valid input from an uploader.json-based remove.conf
    will return a symbolic name
    '''
    for cmd in uploader_json['commands']:
        assert _search_uploader_json(['commands'], cmd['command'])
        assert _search_uploader_json(['commands'], cmd['symbolic_name'])
    for fil in uploader_json['files']:
        assert _search_uploader_json(['files', 'globs'], fil['file'])
        assert _search_uploader_json(['files', 'globs'], fil['symbolic_name'])
    for glb in uploader_json['globs']:
        assert _search_uploader_json(['files', 'globs'], glb['symbolic_name'])


def test_search_uploader_json_invalid():
    '''
    Verify that invalid input will return None
    '''
    assert _search_uploader_json(['commands'], 'random value') is None
    assert _search_uploader_json(['files', 'globs'], 'random value') is None


def test_search_uploader_json_globs_symbolic_only():
    '''
    Verify that globs are matched by symbolic name only
    '''
    for glb in uploader_json['globs']:
        assert _search_uploader_json(['files', 'globs'], glb['glob']) is None


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


@patch('insights.client.map_components._search_uploader_json')
def test_rm_conf_empty(_search_uploader_json):
    '''
    Verify the function returns rm_conf unchanged if called
    with an empty dict or None
    '''
    rm_conf = {}
    new_rm_conf = map_rm_conf_to_components(rm_conf)
    _search_uploader_json.assert_not_called()
    assert new_rm_conf == {}

    rm_conf = None
    new_rm_conf = map_rm_conf_to_components(rm_conf)
    _search_uploader_json.assert_not_called()
    assert new_rm_conf is None


@patch('insights.client.map_components.logger.warning')
def test_log_long_key(logger_warning):
    '''
    Verify the conversion table is logged with proper
    spacing, wrapping, and unconverted specs are not logged
    '''
    rm_conf = {'commands': ["/usr/bin/find /etc/origin/node /etc/origin/master /etc/pki /etc/ipa -type f -exec /usr/bin/openssl x509 -noout -enddate -in '{}' \\; -exec echo 'FileName= {}' \\;",
                            "/usr/bin/md5sum /etc/pki/product/69.pem",
                            "ss_tupna"],
               'files': ["/etc/sysconfig/virt-who",
                         "/etc/yum.repos.d/fedora-cisco-openh264.repo",
                         "krb5_conf_d"]}
    map_rm_conf_to_components(rm_conf)
    logger_warning.assert_any_call("- /usr/bin/find /etc/origin/node                   => certificates_enddate\n  /etc/origin/master /etc/pki /etc/ipa -type f\n  -exec /usr/bin/openssl x509 -noout -enddate -in\n  '{}' \\; -exec echo 'FileName= {}' \\;")
    logger_warning.assert_any_call("- /usr/bin/md5sum /etc/pki/product/69.pem          => md5chk_files")
    logger_warning.assert_any_call("- ss_tupna                                         => ss"),
    logger_warning.assert_any_call("- /etc/sysconfig/virt-who                          => sysconfig_virt_who")
    logger_warning.assert_any_call("- krb5_conf_d                                      => krb5")


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
    rm_conf = {'commands': ["ss_tupna",
                            "/usr/bin/md5sum /etc/pki/product/69.pem"],
               'components': ["insights.specs.default.DefaultSpecs.ss",
                              "insights.specs.default.DefaultSpecs.sysconfig_virt_who"]}
    results = map_rm_conf_to_components(rm_conf)

    assert results == {'commands': [],
                       'files': [],
                       'components': ["insights.specs.default.DefaultSpecs.ss",
                                      "insights.specs.default.DefaultSpecs.sysconfig_virt_who",
                                      "insights.specs.default.DefaultSpecs.md5chk_files"]}
