"""
App manifests for use with the --collector APP option
Define the app manifest and add it to the manifests dict at the bottom of the file
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
        - name: insights.specs.default.DefaultSpecs.bios_uuid
          enabled: true
        - name: insights.specs.Specs.bios_uuid
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

manifests = {'malware-detection': malware_detection_manifest}
content_types = {'malware-detection': 'application/vnd.redhat.malware-detection.results+tgz'}
