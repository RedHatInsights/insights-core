"""
Manifests for supported Apps
============================

For now, the following Apps are supported:

default manifest - for Advisor Rules, no special option
-------------------------------------------------------

malware-detection - "--collector malware-detection"
---------------------------------------------------

compliance - "--compliance"
---------------------------


.. note::
    Define the manifest for the App and add to the manifests `dict` at the
    end of this file.
"""

default_manifest = """
---
# version is for the format of this file, not its contents.
version: 0

client:
  context:
    class: insights.core.context.HostContext
    args:
      timeout: 10 # timeout in seconds for commands. Doesn't apply to files.

  # commands and files to ignore
  blacklist:
    files: []
    commands: []
    patterns: []
    keywords: []

  # Can be a list of dictionaries with name/enabled fields or a list of strings
  # where the string is the name and enabled is assumed to be true. Matching is
  # by prefix, and later entries override previous ones. Persistence for a
  # component is disabled by default.
  persist:
    - name: insights.specs.Specs
      enabled: true

  run_strategy:
    name: serial
    args:
      max_workers: null

plugins:
  # disable everything by default
  # defaults to false if not specified.
  default_component_enabled: false

  # packages and modules to load
  packages:
    - insights.specs.default
    - insights.specs.datasources

  # configuration of loaded components. names are prefixes, so any component with
  # a fully qualified name that starts with a key will get the associated
  # configuration applied. Can specify timeout, which will apply to command
  # datasources. Can specify metadata, which must be a dictionary and will be
  # merged with the components' default metadata.
  configs:
    - name: insights.specs.Specs
      enabled: true
    - name: insights.specs.default.DefaultSpecs
      enabled: true
    - name: insights.specs.datasources
      enabled: true
    # needed for specs that aren't given names before used in DefaultSpecs
    - name: insights.core.spec_factory
      enabled: true

    # needed by multiple datasource specs/components
    - name: insights.parsers.hostname.Hostname
      enabled: true
    - name: insights.parsers.hostname.HostnameDefault
      enabled: true
    - name: insights.combiners.hostname.Hostname
      enabled: true
    - name: insights.parsers.uname.Uname
      enabled: true
    - name: insights.parsers.redhat_release.RedhatRelease
      enabled: true
    - name: insights.combiners.redhat_release.RedHatRelease
      enabled: true
    - name: insights.parsers.ps.PsAuxcww
      enabled: true
    - name: insights.parsers.ps.PsAuxww
      enabled: true
    - name: insights.combiners.ps.Ps
      enabled: true
    - name: insights.parsers.dmidecode.DMIDecode
      enabled: true
    - name: insights.parsers.installed_rpms.InstalledRpms
      enabled: true
    - name: insights.parsers.mount.ProcMounts
      enabled: true

    # needed for identifying RHEL major version
    - name: insights.components.rhel_version.IsRhel6
      enabled: true
    - name: insights.components.rhel_version.IsRhel7
      enabled: true
    - name: insights.components.rhel_version.IsRhel8
      enabled: true
    - name: insights.components.rhel_version.IsRhel9
      enabled: true

    # needed for cloud specs
    - name: insights.parsers.yum.YumRepoList
      enabled: true
    - name: insights.parsers.rhsm_conf.RHSMConf
      enabled: true
    - name: insights.combiners.cloud_provider.CloudProvider
      enabled: true
    - name: insights.components.cloud_provider.IsAWS
      enabled: true
    - name: insights.components.cloud_provider.IsAzure
      enabled: true
    - name: insights.components.cloud_provider.IsGCP
      enabled: true

    # needed for ceph specs
    - name: insights.components.ceph.IsCephMonitor
      enabled: true

    # needed for pcp specs
    - name: insights.parsers.systemd.unitfiles.UnitFiles
      enabled: true
    - name: insights.parsers.ros_config.RosConfig
      enabled: true

    # needed for 'teamdctl_config/state_dump' spec and nmcli_conn_show_uuids spec
    - name: insights.parsers.nmcli.NmcliConnShow
      enabled: true

    # needed for mssql_tls_cert_enddate
    - name: insights.parsers.mssql_conf.MsSQLConf
      enabled: true

    # needed for rsyslog_tls_cert_file
    - name: insights.parsers.rsyslog_conf.RsyslogConf
      enabled: true
    - name: insights.combiners.rsyslog_confs.RsyslogAllConf
      enabled: true

    # needed for sap specs
    - name: insights.parsers.saphostctrl.SAPHostCtrlInstances
      enabled: true
    - name: insights.combiners.sap.Sap
      enabled: true

    # needed for specs: fw_security, smartctl_health
    - name: insights.parsers.virt_what.VirtWhat
      enabled: true
    - name: insights.combiners.virt_what.VirtWhat
      enabled: true
    - name: insights.components.virtualization.IsBareMetal
      enabled: true

    # needed for 'modinfo_filtered_modules' spec
    - name: insights.parsers.lsmod.LsMod
      enabled: true

    # needed for satellite server specs
    - name: insights.combiners.satellite_version.SatelliteVersion
      enabled: true
    - name: insights.combiners.satellite_version.CapsuleVersion
      enabled: true
    - name: insights.components.satellite.IsSatellite
      enabled: true
    - name: insights.components.satellite.IsSatellite614AndLater
      enabled: true
    - name: insights.components.satellite.IsSatelliteLessThan614
      enabled: true
    - name: insights.components.satellite.IsSatellite611
      enabled: true
    - name: insights.components.satellite.IsCapsule
      enabled: true

    # needed for container specs
    - name: insights.parsers.podman_list.PodmanListContainers
      enabled: true
    - name: insights.parsers.docker_list.DockerListContainers
      enabled: true

    # needed for specs: luks_data_sources, smartctl_health spec
    - name: insights.parsers.blkid.BlockIDInfo
      enabled: true
    - name: insights.components.cryptsetup.HasCryptsetupWithTokens
      enabled: true
    - name: insights.components.cryptsetup.HasCryptsetupWithoutTokens
      enabled: true

    # needed for 'iris' specs
    - name: insights.parsers.iris.IrisList
      enabled: true
    - name: insights.parsers.iris.IrisCpf
      enabled: true

    # needed for ausearch_insights
    - name: insights.components.rhel_version.IsGtOrRhel86
      enabled: true

    # needed for spec: subscription_manager_syspurpose
    - name: insights.components.rhel_version.IsGtOrRhel84
      enabled: true

    # needed for sealert spec
    - name: insights.parsers.selinux_config.SelinuxConfig
      enabled: true
    - name: insights.components.selinux.SELinuxEnabled
      enabled: true

    # needed for the 'fstab_mounted.dirs' to the 'ls_lan' spec
    - name: insights.parsers.fstab.FSTab
      enabled: true
""".strip()


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
    - name: insights.specs.Specs.compliance
      enabled: true
    - name: insights.specs.Specs.compliance_policies
      enabled: true
    - name: insights.specs.Specs.compliance_assign
      enabled: true
    - name: insights.specs.Specs.compliance_unassign
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
    - name: insights.specs.Specs.compliance
      enabled: true
    - name: insights.specs.default.DefaultSpecs.compliance
      enabled: true
    - name: insights.specs.default.DefaultSpecs.compliance_policies
      enabled: true
    - name: insights.specs.default.DefaultSpecs.compliance_assign
      enabled: true
    - name: insights.specs.default.DefaultSpecs.compliance_unassign
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
    'default': default_manifest,
    'compliance': compliance_manifest,
    'malware-detection': malware_detection_manifest,
}
"""
Pre-defined manifests for different applications.

    :meta hide-value:
"""
content_types = {
    'default': 'application/vnd.redhat.advisor.collection+tgz',
    'compliance': 'application/vnd.redhat.compliance.something+tgz',
    'malware-detection': 'application/vnd.redhat.malware-detection.results+tgz',
}
"""
Specific content types for uploading data for different applications.

    :meta hide-value:
"""
