import os

# TODO: no bare excepts here
# TODO: maybe call os.makedirs elsewhere
# TODO: copy config file to local config dir if it doesn't exist and --conf is not specified?
# TODO: copy an existing machine-id file to local config dir?
# TODO: set perms on log/lib dirs

_user_home = os.path.expanduser('~')
_app_name = 'insights-client'
_uid = os.getuid()
_user_cache = os.getenv('XDG_CACHE_HOME', default=os.path.join(_user_home, '.cache'))
_etc_insights_client_dir = os.path.join(os.sep, 'etc', 'insights-client')


def _log_dir():
    '''
    Get the insights-client log dir

    Default: /var/log/insights-client
    Non-root user: $XDG_CACHE_HOME/insights-client/log || $HOME/.cache/insights-client/log
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
    Non-root user: $XDG_CACHE_HOME/insights-client/lib || $HOME/.cache/insights-client/lib
    '''
    if _uid == 0:
        insights_lib_dir = os.path.join(os.sep, 'var', 'lib', 'insights')
    else:
        insights_lib_dir = os.path.join(_user_cache, _app_name, 'lib')
    return insights_lib_dir


def _conf_dir():
    if _uid == 0:
        return os.getenv('INSIGHTS_CONF_DIR', default=_etc_insights_client_dir)
    else:
        local_conf_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.join(_user_home, '.config'))
        local_insights_conf_dir = os.path.join(local_conf_dir, _app_name)
        try:
            os.makedirs(local_insights_conf_dir)
        except:
            pass
        return local_insights_conf_dir


def _bc_conf_dir():
    # only needed for .registered files, if run locally just use the
    #   same dir as the default conf dir. It's okay if we write these files twice.
    if _uid == 0:
        return os.path.join(os.sep, 'etc', 'redhat-access-insights')
    else:
        return _conf_dir()


def _var_run_dir():
    if _uid == 0:
        return os.path.join(os.sep, 'var', 'run')
    else:
        return os.path.join(os.sep, 'var', 'run', 'user', str(_uid))


class InsightsConstants(object):
    app_name = _app_name
    auth_method = 'BASIC'
    package_path = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    sleep_time = 180
    command_blacklist = ('rm', 'kill', 'reboot', 'shutdown')
    custom_network_log_level = 11

    # read only files - no local backup needed
    collection_fallback_file = os.path.join(_etc_insights_client_dir, '.fallback.json')
    default_sed_file = os.path.join(_etc_insights_client_dir, '.exp.sed')
    pub_gpg_path = os.path.join(_etc_insights_client_dir, 'redhattools.pub.gpg')
    insights_core_rpm = os.path.join(_etc_insights_client_dir, 'rpm.egg')
    default_egg_gpg_key = os.path.join(_etc_insights_client_dir, 'insights-core.gpg')
    legacy_ca_cert = os.path.join(_etc_insights_client_dir, 'cert-api.access.redhat.com.pem')
    machine_id_file = os.path.join(_etc_insights_client_dir, 'machine-id')

    # read/write etc files
    default_conf_dir = _conf_dir()
    simple_find_replace_dir = _bc_conf_dir()
    default_conf_file = os.path.join(default_conf_dir, 'insights-client.conf')
    default_tags_file = os.path.join(default_conf_dir, 'tags.yaml')
    simple_find_replace_dir = _bc_conf_dir()
    custom_network_log_level = 11
    collection_rules_file = os.path.join(default_conf_dir, '.cache.json')
    unregistered_files = [os.path.join(default_conf_dir, '.unregistered'),
                          os.path.join(simple_find_replace_dir, '.unregistered')]
    registered_files = [os.path.join(default_conf_dir, '.registered'),
                        os.path.join(simple_find_replace_dir, '.registered')]
    lastupload_file = os.path.join(default_conf_dir, '.lastupload')
    core_etag_file = os.path.join(default_conf_dir, '.insights-core.etag')
    core_gpg_sig_etag_file = os.path.join(default_conf_dir, '.insights-core-gpg-sig.etag')
    last_upload_results_file = os.path.join(default_conf_dir, '.last-upload.results')
    cached_branch_info = os.path.join(default_conf_dir, '.branch_info')

    # read/write lib files
    insights_core_lib_dir = _lib_dir()
    insights_core_last_stable = os.path.join(insights_core_lib_dir, 'last_stable.egg')
    insights_core_last_stable_gpg_sig = os.path.join(insights_core_lib_dir, 'last_stable.egg.asc')
    insights_core_newest = os.path.join(insights_core_lib_dir, 'newest.egg')
    insights_core_gpg_sig_newest = os.path.join(insights_core_lib_dir, 'newest.egg.asc')

    # log files
    log_dir = _log_dir()
    default_log_file = os.path.join(log_dir, app_name + '.log')
    default_payload_log = os.path.join(log_dir, app_name + '-payload.log')

    # other
    pidfile = os.path.join(_var_run_dir(), 'insights-client.pid')
    ppidfile = os.path.join(os.sep, 'tmp', 'insights-client.ppid')

    base_url = 'cert-api.access.redhat.com/r/insights/platform'
    legacy_base_url = 'cert-api.access.redhat.com/r/insights'
    default_branch_info = {'remote_branch': -1, 'remote_leaf': -1}
    default_cmd_timeout = 120  # default command execution to two minutes, prevents long running commands that will hang
    module_router_path = "/module-update-router/v1/channel?module=insights-core"
    sig_kill_ok = 100
    sig_kill_bad = 101
    egg_release_file = os.path.join(os.sep, 'tmp', 'insights-client-egg-release')
    valid_compressors = ("gz", "xz", "bz2", "none")
    # RPM version in which core collection was released
    core_collect_rpm_version = '3.1.0'
