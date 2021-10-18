"""
App default manifests for use with the --collector APP option
Define the app manifest and add it to the manifests dict at the bottom of the file
"""

malware_default_manifest = """
# Manifest file for malware data collection
---
# version is for the format of this file, not its contents.
version: 0
content_type: application/vnd.redhat.malware.results+tgz

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
        - name: insights.specs.malware.MalwareSpecs
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
        - insights.specs.malware
        - insights.specs.default
    configs:
        # determines which specs get loaded
        - name: insights.specs.malware.MalwareSpecs
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

default_manifests = {'malware': malware_default_manifest}