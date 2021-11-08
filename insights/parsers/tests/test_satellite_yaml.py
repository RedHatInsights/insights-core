import doctest

from insights.tests import context_wrap
from insights.parsers import satellite_yaml


SATELLITE_YAML_FILE_CONTENT = """
---
:answer_file: "/etc/foreman-installer/scenarios.d/satellite-answers.yaml"
:color_of_background: :dark
:colors: true
:custom:
  :lock_package_versions: true
:description: Install Satellite server
:dont_save_answers: false
:enabled: true
:facts:
  tuning: default
  mongo_cache_size: 3.89
:hiera_config: "/usr/share/foreman-installer/config/foreman-hiera.yaml"
:hook_dirs:
- "/usr/share/foreman-installer/katello/hooks"
:ignore_undocumented: false
:installer_dir: "/usr/share/foreman-installer"
:log_dir: "/var/log/foreman-installer"
:log_level: DEBUG
:log_name: satellite.log
:low_priority_modules: []
:mapping: {}
:module_dirs: "/usr/share/foreman-installer/modules"
:name: Satellite
:no_prefix: false
:order:
- certs
- foreman
- katello
- foreman_proxy
- foreman_proxy::plugin::pulp
- foreman_proxy_content
- puppet
:parser_cache_path:
- "/usr/share/foreman-installer/parser_cache/foreman.yaml"
- "/usr/share/foreman-installer/parser_cache/katello.yaml"
:skip_puppet_version_check: false
:store_dir: ''
:verbose: true
:verbose_log_level: notice
""".strip()

sat_yaml_path = "/etc/foreman-installer/scenarios.d/satellite.yaml"


def test_satellite_yaml():
    result = satellite_yaml.SatelliteYaml(
        context_wrap(SATELLITE_YAML_FILE_CONTENT, path=sat_yaml_path)
    )
    assert ':facts' in result
    assert result[':facts']['tuning'] == 'default'


def test_doc():
    failed_count, tests = doctest.testmod(
        satellite_yaml,
        globs={
            "SatelliteYaml": satellite_yaml.SatelliteYaml(context_wrap(SATELLITE_YAML_FILE_CONTENT))
        },
    )
    assert failed_count == 0
