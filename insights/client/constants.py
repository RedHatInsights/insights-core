import os


class InsightsConstants(object):
    app_name = 'insights-client'
    version = '3.0.0-2'
    auth_method = 'BASIC'
    package_path = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    sleep_time = 300
    default_conf_file = '/etc/insights-client/insights-client.conf'
    user_agent = os.path.join(app_name, version)
    log_dir = os.path.join(os.sep, 'var', 'log', app_name)
    default_conf_dir = '/etc/insights-client'
    default_sed_file = os.path.join(default_conf_dir, '.exp.sed')
    base_url = ''
    collection_rules_file = os.path.join(default_conf_dir, '.cache.json')
    collection_fallback_file = os.path.join(default_conf_dir, '.fallback.json')
    collection_remove_file_name = 'remove.conf'
    collection_remove_file = os.path.join(default_conf_dir, collection_remove_file_name)
    unregistered_file = os.path.join(default_conf_dir, '.unregistered')
    registered_file = os.path.join(default_conf_dir, '.registered')
    lastupload_file = os.path.join(default_conf_dir, '.lastupload')
    pub_gpg_path = os.path.join(default_conf_dir, 'redhattools.pub.gpg')
    machine_id_file = os.path.join(default_conf_dir, 'machine-id')
    docker_group_id_file = os.path.join(default_conf_dir, 'docker-group-id')
    default_target = [{'type': 'host', 'name': ''}]
    default_branch_info = {'remote_branch': -1, 'remote_leaf': -1}
    docker_image_name = None
    default_cmd_timeout = 600  # default command execution to ten minutes, prevents long running commands that will hang
    default_egg_gpg_key = os.path.join(default_conf_dir, 'insights-core.gpg')
    core_etag_file = os.path.join(default_conf_dir, '.insights-core.etag')
    core_gpg_sig_etag_file = os.path.join(default_conf_dir, '.insights-core-gpg-sig.etag')
    last_upload_results_file = os.path.join(default_conf_dir, '.last-upload.results')
    insights_ansible_facts_dir = os.path.join('/', 'etc', 'ansible', 'facts.d')
    insights_ansible_facts_file = os.path.join(insights_ansible_facts_dir, 'insights.fact')
    insights_ansible_machine_id_file = os.path.join(insights_ansible_facts_dir, 'insights_machine_id.fact')
    insights_core_lib_dir = os.path.join('/', 'var', 'lib', 'insights')
    insights_core_rpm = os.path.join(default_conf_dir, 'rpm.egg')
    insights_core_last_stable = os.path.join(insights_core_lib_dir, 'last_stable.egg')
    insights_core_last_stable_gpg_sig = os.path.join(insights_core_lib_dir, 'last_stable.egg.asc')
    insights_core_newest = os.path.join(insights_core_lib_dir, 'newest.egg')
    insights_core_gpg_sig_newest = os.path.join(insights_core_lib_dir, 'newest.egg.asc')
    sig_kill_ok = 100
    sig_kill_bad = 101
