import os

_user_home = os.path.expanduser('~')
_app_name = 'insights-client'
_uid = os.getuid()
_user_cache = os.getenv('XDG_CACHE_HOME', default=os.path.join(_user_home, '.cache'))


def _log_dir():
    '''
    Get the insights-client log dir

    Default: /var/log/insights-client
    Non-root user: $XDG_CACHE_HOME/insights-client || $HOME/.cache/insights-client/log
    '''
    if _uid == 0:
        insights_log_dir = os.path.join(os.sep, 'var', 'log', _app_name)
    else:
        insights_log_dir = os.path.join(_user_cache, _app_name, 'log')
    return insights_log_dir


def _lib_dir():
    '''
    Get the insights-client egg cache dir

    Default: /var/lib/insights
    Non-root user: $XDG_CACHE_HOME/insights-client || $HOME/.cache/insights-client/lib
    '''
    if _uid == 0:
        insights_lib_dir = os.path.join(os.sep, 'var', 'lib', 'insights')
    else:
        insights_lib_dir = os.path.join(_user_cache, _app_name, 'lib')
    return insights_lib_dir


class InsightsConstants(object):
    app_name = _app_name
    auth_method = 'BASIC'
    package_path = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    sleep_time = 180
    command_blacklist = ('rm', 'kill', 'reboot', 'shutdown')
    default_conf_dir = os.getenv('INSIGHTS_CONF_DIR', default='/etc/insights-client')
    default_conf_file = os.path.join(default_conf_dir, 'insights-client.conf')
    default_tags_file = os.path.join(default_conf_dir, 'tags.yaml')
    log_dir = _log_dir()
    simple_find_replace_dir = '/etc/redhat-access-insights'
    default_log_file = os.path.join(log_dir, app_name + '.log')
    default_payload_log = os.path.join(log_dir, app_name + '-payload.log')
    custom_network_log_level = 11
    default_sed_file = os.path.join(default_conf_dir, '.exp.sed')
    base_url = 'cert-api.access.redhat.com/r/insights/platform'
    legacy_base_url = 'cert-api.access.redhat.com/r/insights'
    collection_rules_file = os.path.join(default_conf_dir, '.cache.json')
    collection_fallback_file = os.path.join(default_conf_dir, '.fallback.json')
    unregistered_files = [os.path.join(default_conf_dir, '.unregistered'),
                          os.path.join(simple_find_replace_dir, '.unregistered')]
    registered_files = [os.path.join(default_conf_dir, '.registered'),
                        os.path.join(simple_find_replace_dir, '.registered')]
    lastupload_file = os.path.join(default_conf_dir, '.lastupload')
    pub_gpg_path = os.path.join(default_conf_dir, 'redhattools.pub.gpg')
    machine_id_file = os.path.join(default_conf_dir, 'machine-id')
    default_branch_info = {'remote_branch': -1, 'remote_leaf': -1}
    default_cmd_timeout = 120  # default command execution to two minutes, prevents long running commands that will hang
    default_egg_gpg_key = os.path.join(default_conf_dir, 'insights-core.gpg')
    core_etag_file = os.path.join(default_conf_dir, '.insights-core.etag')
    core_gpg_sig_etag_file = os.path.join(default_conf_dir, '.insights-core-gpg-sig.etag')
    last_upload_results_file = os.path.join(default_conf_dir, '.last-upload.results')
    insights_core_lib_dir = _lib_dir()
    insights_core_rpm = os.path.join(default_conf_dir, 'rpm.egg')
    insights_core_last_stable = os.path.join(insights_core_lib_dir, 'last_stable.egg')
    insights_core_last_stable_gpg_sig = os.path.join(insights_core_lib_dir, 'last_stable.egg.asc')
    insights_core_newest = os.path.join(insights_core_lib_dir, 'newest.egg')
    insights_core_gpg_sig_newest = os.path.join(insights_core_lib_dir, 'newest.egg.asc')
    module_router_path = "/module-update-router/v1/channel?module=insights-core"
    sig_kill_ok = 100
    sig_kill_bad = 101
    cached_branch_info = os.path.join(default_conf_dir, '.branch_info')
    pidfile = os.path.join(os.sep, 'var', 'run', 'insights-client.pid')
    insights_tmp_path = os.path.join(os.sep, 'var', 'tmp')
    insights_tmp_prefix = 'insights-client'
    egg_release_file = os.path.join(os.sep, insights_tmp_path, insights_tmp_prefix, 'insights-client-egg-release')
    ppidfile = os.path.join(os.sep, 'tmp', 'insights-client.ppid')
    valid_compressors = ("gz", "xz", "bz2", "none")
    # RPM version in which core collection was released
    core_collect_rpm_version = '3.1.0'
    # RPM version in which logrotate was released
    rpm_version_before_logrotate = '3.2.0'
    rhsm_facts_dir = os.path.join(os.sep, 'etc', 'rhsm', 'facts')
    rhsm_facts_file = os.path.join(os.sep, 'etc', 'rhsm', 'facts', 'insights-client.facts')
    # In MB
    archive_filesize_max = 100
