"""
Manifests for supported Apps
============================

For now, the following Apps are supported:

malware-detection - "--collector malware-detection"
---------------------------------------------------

compliance - "--compliance"
---------------------------


Note: Define the manifest for the app and add it to the manifests dict at the
bottom of the file.
"""

malware_detection_manifest = """
# Manifest file for malware detection app data collection
---
# version is for the format of this file, not its contents.
version: 0

client:
  context:
    class: insights.core.context.HostContext
    args:
      timeout: 10 # timeout in seconds for commands. Doesn't apply to files.

  blacklist:
    files: []
    commands: []
    patterns: []
    keywords: []

  persist:
    # determines what will appear in the archive
    - name: insights.specs.default.DefaultSpecs.malware_detection
      enabled: true

  run_strategy:
    name: serial
    args:
      max_workers: null

plugins:
  # disable everything by default
  # defaults to false if not specified.
  default_component_enabled: false
  packages:
    # determines which packages are loaded. These will be namespaced to the relevant collector
    - insights.specs.datasources.malware_detection
    - insights.specs.default
  configs:
    # determines which specs get loaded
    - name: insights.specs.default.DefaultSpecs.malware_detection
      enabled: true
    # Enable specs for collecting the system's canonical facts
    - name: insights.specs.default.DefaultSpecs.mac_addresses
      enabled: true
    - name: insights.specs.Specs.mac_addresses
      enabled: true
    - name: insights.specs.default.DefaultSpecs.etc_machine_id
      enabled: true
    - name: insights.specs.Specs.etc_machine_id
      enabled: true
    - name: insights.specs.default.DefaultSpecs.hostname
      enabled: true
    - name: insights.specs.Specs.hostname
      enabled: true
    - name: insights.specs.default.DefaultSpecs.dmidecode
      enabled: true
    - name: insights.specs.Specs.dmidecode
      enabled: true
    - name: insights.specs.default.DefaultSpecs.machine_id
      enabled: true
    - name: insights.specs.Specs.machine_id
      enabled: true
    - name: insights.specs.default.DefaultSpecs.ip_addresses
      enabled: true
    - name: insights.specs.Specs.ip_addresses
      enabled: true
    - name: insights.specs.default.DefaultSpecs.subscription_manager_id
      enabled: true
    - name: insights.specs.Specs.subscription_manager_id
      enabled: true
""".lstrip()

compliance_manifest = """
# Manifest file for compliance data collection
---
# version is for the format of this file, not its contents.
version: 0

client:
  context:
    class: insights.core.context.HostContext
    args:
      timeout: 10 # timeout in seconds for commands. Doesn't apply to files.

  blacklist:
    files: []
    commands: []
    patterns: []
    keywords: []

  persist:
    # determines what will appear in the archive
    - name: insights.specs.default.DefaultSpecs.compliance
      enabled: true

  run_strategy:
    name: serial
    args:
      max_workers: null

plugins:
  # disable everything by default
  # defaults to false if not specified.
  default_component_enabled: false
  packages:
    # determines which packages are loaded. These will be namespaced to the relevant collector
    - insights.specs.datasources.compliance
    - insights.specs.default
  configs:
    # determines which specs get loaded
    - name: insights.specs.datasources.compliance.compliance_ds
      enabled: true
    - name: insights.specs.default.DefaultSpecs.compliance
      enabled: true

    # Enable specs for collecting the system's canonical facts
    - name: insights.specs.default.DefaultSpecs.mac_addresses
      enabled: true
    - name: insights.specs.Specs.mac_addresses
      enabled: true
    - name: insights.specs.default.DefaultSpecs.etc_machine_id
      enabled: true
    - name: insights.specs.Specs.etc_machine_id
      enabled: true
    - name: insights.specs.default.DefaultSpecs.hostname
      enabled: true
    - name: insights.specs.Specs.hostname
      enabled: true
    - name: insights.specs.default.DefaultSpecs.dmidecode
      enabled: true
    - name: insights.specs.Specs.dmidecode
      enabled: true
    - name: insights.specs.default.DefaultSpecs.machine_id
      enabled: true
    - name: insights.specs.Specs.machine_id
      enabled: true
    - name: insights.specs.default.DefaultSpecs.ip_addresses
      enabled: true
    - name: insights.specs.Specs.ip_addresses
      enabled: true
    - name: insights.specs.default.DefaultSpecs.subscription_manager_id
      enabled: true
    - name: insights.specs.Specs.subscription_manager_id
      enabled: true
    - name: insights.specs.Specs.redhat_release
      enabled: true
    - name: insights.specs.default.DefaultSpecs.redhat_release
      enabled: true
    - name: insights.specs.Specs.os_release
      enabled: true
    - name: insights.specs.default.DefaultSpecs.os_release
      enabled: true
    - name: insights.parsers.redhat_release.RedhatRelease
      enabled: true
    - name: insights.parsers.os_release.OsRelease
      enabled: true
    - name: insights.specs.Specs.installed_rpms
      enabled: true
    - name: insights.specs.default.DefaultSpecs.installed_rpms
      enabled: true
    - name: insights.parsers.installed_rpms.InstalledRpms
      enabled: true
""".lstrip()

manifests = {
    'compliance': compliance_manifest,
    'malware-detection': malware_detection_manifest
}
content_types = {
    'compliance': 'application/vnd.redhat.compliance.something+tgz',
    'malware-detection': 'application/vnd.redhat.malware-detection.results+tgz',
}
