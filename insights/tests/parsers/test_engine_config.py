from insights.parsers.engine_config import EngineConfigAll
from insights.tests import context_wrap


ENGINE_CONFIG_ALL_OUTPUT = """
AffinityRulesEnforcementManagerEnabled: true version: general
AffinityRulesEnforcementManagerRegularInterval: 1 version: general
AsyncTaskPollingRate: 10 version: general
AsyncTaskZombieTaskLifeInMinutes: 3000 version: general
AuditLogAgingThreshold: 30 version: general
AuditLogCleanupTime: 03:35:35 version: general
BlockMigrationOnSwapUsagePercentage: 0 version: general
BootstrapMinimalVdsmVersion: 4.9 version: general
CpuOverCommitDurationMinutes: 2 version: general
DisableFenceAtStartupInSec: 300 version: general
PopulateDirectLUNDiskDescriptionWithLUNId: 4 version: general
MaxBlockDiskSize: 8192 version: general
ClusterEmulatedMachines: pc-i440fx-rhel7.2.0,pseries-rhel7.2.0 version: 3.6
ClusterEmulatedMachines: pc-i440fx-rhel7.2.0,pseries-rhel7.2.0 version: 4.0
ClusterEmulatedMachines: pc-i440fx-rhel7.3.0,pc-i440fx-2.6,pseries-rhel7.3.0 version: 4.1
ClusterEmulatedMachines: rhel6.2.0 version: 3.0
ClusterEmulatedMachines: rhel6.3.0 version: 3.1
ClusterEmulatedMachines: rhel6.4.0 version: 3.2
ClusterEmulatedMachines: rhel6.5.0 version: 3.3
ClusterEmulatedMachines: rhel6.5.0,pseries version: 3.4
ClusterEmulatedMachines: rhel6.5.0,pseries version: 3.5
WANDisableEffects: animation version: general
WANColorDepth: 16 version: general
EnableSpiceRootCertificateValidation: true version: general
EnableUSBAsDefault: true version: general
EnableVdsLoadBalancing: true version: general
EncryptHostCommunication: true version: general
ExternalCommunicationProtocol: TLSv1.2 version: general
CriticalSpaceActionBlocker: 5 version: general
WarningLowSpaceIndicator: 10 version: general
HighUtilizationForEvenlyDistribute: 75 version: general
HighUtilizationForPowerSave: 75 version: general
LogPhysicalMemoryThresholdInMB: 1024 version: general
LowUtilizationForEvenlyDistribute: 0 version: general
LowUtilizationForPowerSave: 20 version: general
MaxNumberOfHostsInStoragePool: 250 version: general
MaxNumOfCpuPerSocket: 16 version: 3.6
MaxNumOfCpuPerSocket: 16 version: 4.0
MaxNumOfCpuPerSocket: 254 version: 4.1
MaxNumOfThreadsPerCpu: 8 version: 3.6
MaxNumOfThreadsPerCpu: 8 version: 4.0
MaxNumOfThreadsPerCpu: 8 version: 4.1
MaxNumOfVmCpus: 240 version: 3.6
MaxNumOfVmCpus: 240 version: 4.0
MaxNumOfVmCpus: 288 version: 4.1
MaxNumOfVmSockets: 16 version: 3.6
MaxNumOfVmSockets: 16 version: 4.0
AffMaxNumOfVmSockets: 16 version: 4.1
MaxRerunVmOnVdsCount: 3 version: general
MaxSchedulerWeight: 1000 version: general
MaxStorageVdsDelayCheckSec: 5 version: general
MaxStorageVdsTimeoutCheckSec: 30 version: general
MaxVdsMemOverCommit: 200 version: general
MaxVdsMemOverCommitForServers: 150 version: general
MaxVdsNameLength: 255 version: general
MaxVmNameLength: 64 version: general
MaxVmNameLengthSysprep: 15 version: general
MaxVmsInPool: 1000 version: general
VmPoolMaxSubsequentFailures: 3 version: general
NumberOfFailedRunsOnVds: 3 version: general
NumberVmRefreshesBeforeSave: 5 version: general
oVirtISOsRepositoryPath: /usr/share/ovirt-node-iso:/usr/share/rhev-hypervisor version: general
OvfItemsCountPerUpdate: 100 version: general
OvfUpdateIntervalInMinutes: 60 version: general
StorageDomainOvfStoreCount: 2 version: general
ProductRPMVersion: 4.1.8.2-0.1.el7 version: general
SANWipeAfterDelete: false version: general
SearchResultsLimit: 100 version: general
ServerRebootTimeout: 300 version: general
ConsoleReleaseCursorKeys: shift+f12 version: general
ConsoleToggleFullScreenKeys: shift+f11 version: general
SpiceUsbAutoShare: true version: general
FullScreenWebadminDefault: false version: general
FullScreenUserportalBasicDefault: true version: general
FullScreenUserportalExtendedDefault: false version: general
SpmCommandFailOverRetries: 3 version: general
SPMFailOverAttempts: 3 version: general
SpmVCpuConsumption: 1 version: general
SSHInactivityTimeoutSeconds: 300 version: general
SSHInactivityHardTimeoutSeconds: 1800 version: general
NumberOfUSBSlots: 4 version: general
SSLEnabled: true version: general
StorageDomainFailureTimeoutInMinutes: 5 version: general
StoragePoolRefreshTimeInSeconds: 10 version: general
TimeoutToResetVdsInSeconds: 60 version: general
DelayResetForSpmInSeconds: 20 version: general
DelayResetPerVmInSeconds: 0.5 version: general
TimeToReduceFailedRunOnVdsInMinutes: 30 version: general
UserDefinedVMProperties:  version: 3.6
UserDefinedVMProperties:  version: 4.0
UserDefinedVMProperties:  version: 4.1
UtilizationThresholdInPercent: 80 version: general
ValidNumOfMonitors: 1,2,4 version: general
VdcVersion: 4.1.0.0 version: general
VDSAttemptsToResetCount: 2 version: general
VdsLoadBalancingIntervalInMinutes: 1 version: general
VdsRecoveryTimeoutInMinutes: 3 version: general
VdsRefreshRate: 3 version: general
vdsTimeout: 180 version: general
vdsConnectionTimeout: 20 version: general
vdsRetries: 0 version: general
EventProcessingPoolSize: 10 version: general
VmGracefulShutdownMessage: System Administrator has initiated shutdown of this Virtual Machine. Virtual Machine is shutting down. version: general
VmGracefulShutdownTimeout: 30 version: general
VM32BitMaxMemorySizeInMB: 20480 version: general
VM64BitMaxMemorySizeInMB: 4194304 version: 3.6
VM64BitMaxMemorySizeInMB: 4194304 version: 4.0
VM64BitMaxMemorySizeInMB: 4194304 version: 4.1
MaxMemorySlots: 16 version: general
HotPlugMemoryMultiplicationSizeMb: 256 version: general
VncKeyboardLayout: en-us version: general
WaitForVdsInitInSec: 60 version: general
FenceQuietTimeBetweenOperationsInSec: 180 version: general
FenceProxyDefaultPreferences: cluster,dc version: general
MaxAuditLogMessageLength: 10000 version: general
SysPrepDefaultUser:  version: general
SysPrepDefaultPassword: Empty version: general
UserSessionTimeOutInterval: 30 version: general
IPTablesConfig:
# oVirt default firewall configuration. Automatically generated by vdsm bootstrap script.
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -i lo -j ACCEPT
# vdsm
-A INPUT -p tcp --dport @VDSM_PORT@ -j ACCEPT
# ovirt-imageio-daemon
-A INPUT -p tcp --dport 54322 -j ACCEPT
# rpc.statd
-A INPUT -p tcp --dport 111 -j ACCEPT
-A INPUT -p udp --dport 111 -j ACCEPT
# SSH
-A INPUT -p tcp --dport @SSH_PORT@ -j ACCEPT
# snmp
-A INPUT -p udp --dport 161 -j ACCEPT
# Cockpit
-A INPUT -p tcp --dport 9090 -j ACCEPT

@CUSTOM_RULES@

# Reject any other input traffic
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -m physdev ! --physdev-is-bridged -j REJECT --reject-with icmp-host-prohibited
COMMIT
 version: general
IPTablesConfigSiteCustom:  version: general
OvirtIsoPrefix: ^ovirt-node-iso-([0-9].*)\.iso$:^rhevh-([0-9].*)\.iso$ version: general
OvirtInitialSupportedIsoVersion: 2.5.5:5.8 version: general
VdsLocalDisksLowFreeSpace: 500 version: general
VdsLocalDisksCriticallyLowFreeSpace: 500 version: general
JobCleanupRateInMinutes: 10 version: general
SucceededJobCleanupTimeInMinutes: 10 version: general
FailedJobCleanupTimeInMinutes: 60 version: general
VmPoolMonitorIntervalInMinutes: 5 version: general
VmPoolMonitorBatchSize: 5 version: general
NetworkConnectivityCheckTimeoutInSeconds: 120 version: general
AllowClusterWithVirtGlusterEnabled: true version: general
EnableMACAntiSpoofingFilterRules: true version: general
EnableHostTimeDrift: true version: general
EngineMode: Active version: general
HostTimeDriftInSec: 300 version: general
LogMaxPhysicalMemoryUsedThresholdInPercentage: 95 version: general
LogMaxCpuUsedThresholdInPercentage: 95 version: general
LogMaxNetworkUsedThresholdInPercentage: 95 version: general
LogMinFreeSwapThresholdInMB: 256 version: general
LogMaxSwapUsedThresholdInPercentage: 95 version: general
SpiceProxyDefault:  version: general
RemoteViewerSupportedVersions: rhev-win64:2.0-160;rhev-win32:2.0-160;rhel7:2.0-6;rhel6:99.0-1 version: general
RemoteViewerNewerVersionUrl: ${console_client_resources_url} version: general
RemapCtrlAltDelDefault: true version: general
ClientModeSpiceDefault: Native version: general
ClientModeVncDefault: Native version: general
ClientModeRdpDefault: Auto version: general
WebSocketProxy: rhevm.example.com:6100 version: general
WebSocketProxyTicketValiditySeconds: 120 version: general
CustomDeviceProperties: {type=interface;prop={SecurityGroups=^(?:(?:[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}, *)*[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}|)$}} version: 3.6
CustomDeviceProperties: {type=interface;prop={SecurityGroups=^(?:(?:[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}, *)*[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}|)$}} version: 4.0
CustomDeviceProperties: {type=interface;prop={SecurityGroups=^(?:(?:[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}, *)*[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}|)$}} version: 4.1
UserDefinedNetworkCustomProperties:  version: 3.6
UserDefinedNetworkCustomProperties:  version: 4.0
UserDefinedNetworkCustomProperties:  version: 4.1
GlusterRefreshRateHooks: 7200 version: general
DefaultWindowsTimeZone: GMT Standard Time version: general
DefaultGeneralTimeZone: Etc/GMT version: general
OnlyRequiredNetworksMandatoryForVdsSelection: false version: general
MaxAverageNetworkQoSValue: 1024 version: general
MaxPeakNetworkQoSValue: 2048 version: general
MaxBurstNetworkQoSValue: 10240 version: general
MaxHostNetworkQosShares: 100 version: general
DisplayUncaughtUIExceptions: true version: general
QoSInboundAverageDefaultValue: 10 version: general
QoSInboundPeakDefaultValue: 10 version: general
QoSInboundBurstDefaultValue: 100 version: general
QoSOutboundAverageDefaultValue: 10 version: general
QoSOutboundPeakDefaultValue: 10 version: general
QoSOutboundBurstDefaultValue: 100 version: general
SecureConnectionWithOATServers: true version: general
PollUri: AttestationService/resources/PollHosts version: general
AttestationTruststore: TrustStore.jks version: general
AttestationPort: 8443 version: general
AttestationTruststorePass:  version: general
AttestationServer:  version: general
AttestationFirstStageSize: 10 version: general
ExternalSchedulerServiceURL: http://localhost:18781/ version: general
ExternalSchedulerConnectionTimeout: 100 version: general
ExternalSchedulerEnabled: false version: general
ExternalSchedulerResponseTimeout: 120000 version: general
DwhHeartBeatInterval: 15 version: general
HostPreparingForMaintenanceIdleTime: 300 version: general
UseFqdnForRdpIfAvailable: true version: general
SpeedOptimizationSchedulingThreshold: 10 version: general
SchedulerAllowOverBooking: false version: general
SchedulerOverBookingThreshold: 10 version: general
OverUtilizationForHaReservation: 200 version: general
ScaleDownForHaReservation: 1 version: general
VdsHaReservationIntervalInMinutes: 5 version: general
DefaultMaximumMigrationDowntime: 0 version: general
DefaultSerialNumberPolicy: HOST_ID version: general
MigrationPolicies: [{"id":{"uuid":"80554327-0569-496b-bdeb-fcbbf52b827b"},"maxMigrations":2,"autoConvergence":true,"migrationCompression":false,"enableGuestEvents":true,"name":"Minimal downtime","description":"A policy that lets the VM migrate in typical situations. The VM should not experience any significant downtime. If the VM migration is not converging for a long time, the migration will be aborted. The guest agent hook mechanism is enabled.","config":{"convergenceItems":[{"stallingLimit":1,"convergenceItem":{"action":"setDowntime","params":["150"]}},{"stallingLimit":2,"convergenceItem":{"action":"setDowntime","params":["200"]}},{"stallingLimit":3,"convergenceItem":{"action":"setDowntime","params":["300"]}},{"stallingLimit":4,"convergenceItem":{"action":"setDowntime","params":["400"]}},{"stallingLimit":6,"convergenceItem":{"action":"setDowntime","params":["500"]}}],"initialItems":[{"action":"setDowntime","params":["100"]}],"lastItems":[{"action":"abort","params":[]}]}},{"id":{"uuid":"80554327-0569-496b-bdeb-fcbbf52b827c"},"maxMigrations":1,"autoConvergence":true,"migrationCompression":true,"enableGuestEvents":true,"name":"Suspend workload if needed","description":"A policy that lets the VM migrate in most situations, including VMs running heavy workloads. On the other hand, the VM may experience a more significant downtime. The migration may still be aborted for extreme workloads. The guest agent hook mechanism is enabled.","config":{"convergenceItems":[{"stallingLimit":1,"convergenceItem":{"action":"setDowntime","params":["150"]}},{"stallingLimit":2,"convergenceItem":{"action":"setDowntime","params":["200"]}},{"stallingLimit":3,"convergenceItem":{"action":"setDowntime","params":["300"]}},{"stallingLimit":4,"convergenceItem":{"action":"setDowntime","params":["400"]}},{"stallingLimit":6,"convergenceItem":{"action":"setDowntime","params":["500"]}}],"initialItems":[{"action":"setDowntime","params":["100"]}],"lastItems":[{"action":"setDowntime","params":["5000"]},{"action":"abort","params":[]}]}}] version: 3.6
MigrationPolicies: [{"id":{"uuid":"80554327-0569-496b-bdeb-fcbbf52b827b"},"maxMigrations":2,"autoConvergence":true,"migrationCompression":false,"enableGuestEvents":true,"name":"Minimal downtime","description":"A policy that lets the VM migrate in typical situations. The VM should not experience any significant downtime. If the VM migration is not converging for a long time, the migration will be aborted. The guest agent hook mechanism is enabled.","config":{"convergenceItems":[{"stallingLimit":1,"convergenceItem":{"action":"setDowntime","params":["150"]}},{"stallingLimit":2,"convergenceItem":{"action":"setDowntime","params":["200"]}},{"stallingLimit":3,"convergenceItem":{"action":"setDowntime","params":["300"]}},{"stallingLimit":4,"convergenceItem":{"action":"setDowntime","params":["400"]}},{"stallingLimit":6,"convergenceItem":{"action":"setDowntime","params":["500"]}}],"initialItems":[{"action":"setDowntime","params":["100"]}],"lastItems":[{"action":"abort","params":[]}]}},{"id":{"uuid":"80554327-0569-496b-bdeb-fcbbf52b827c"},"maxMigrations":1,"autoConvergence":true,"migrationCompression":true,"enableGuestEvents":true,"name":"Suspend workload if needed","description":"A policy that lets the VM migrate in most situations, including VMs running heavy workloads. On the other hand, the VM may experience a more significant downtime. The migration may still be aborted for extreme workloads. The guest agent hook mechanism is enabled.","config":{"convergenceItems":[{"stallingLimit":1,"convergenceItem":{"action":"setDowntime","params":["150"]}},{"stallingLimit":2,"convergenceItem":{"action":"setDowntime","params":["200"]}},{"stallingLimit":3,"convergenceItem":{"action":"setDowntime","params":["300"]}},{"stallingLimit":4,"convergenceItem":{"action":"setDowntime","params":["400"]}},{"stallingLimit":6,"convergenceItem":{"action":"setDowntime","params":["500"]}}],"initialItems":[{"action":"setDowntime","params":["100"]}],"lastItems":[{"action":"setDowntime","params":["5000"]},{"action":"abort","params":[]}]}}] version: 4.0
MigrationPolicies: [{"id":{"uuid":"80554327-0569-496b-bdeb-fcbbf52b827b"},"maxMigrations":2,"autoConvergence":true,"migrationCompression":false,"enableGuestEvents":true,"name":"Minimal downtime","description":"A policy that lets the VM migrate in typical situations. The VM should not experience any significant downtime. If the VM migration is not converging for a long time, the migration will be aborted. The guest agent hook mechanism is enabled.","config":{"convergenceItems":[{"stallingLimit":1,"convergenceItem":{"action":"setDowntime","params":["150"]}},{"stallingLimit":2,"convergenceItem":{"action":"setDowntime","params":["200"]}},{"stallingLimit":3,"convergenceItem":{"action":"setDowntime","params":["300"]}},{"stallingLimit":4,"convergenceItem":{"action":"setDowntime","params":["400"]}},{"stallingLimit":6,"convergenceItem":{"action":"setDowntime","params":["500"]}}],"initialItems":[{"action":"setDowntime","params":["100"]}],"lastItems":[{"action":"abort","params":[]}]}},{"id":{"uuid":"80554327-0569-496b-bdeb-fcbbf52b827c"},"maxMigrations":1,"autoConvergence":true,"migrationCompression":true,"enableGuestEvents":true,"name":"Suspend workload if needed","description":"A policy that lets the VM migrate in most situations, including VMs running heavy workloads. On the other hand, the VM may experience a more significant downtime. The migration may still be aborted for extreme workloads. The guest agent hook mechanism is enabled.","config":{"convergenceItems":[{"stallingLimit":1,"convergenceItem":{"action":"setDowntime","params":["150"]}},{"stallingLimit":2,"convergenceItem":{"action":"setDowntime","params":["200"]}},{"stallingLimit":3,"convergenceItem":{"action":"setDowntime","params":["300"]}},{"stallingLimit":4,"convergenceItem":{"action":"setDowntime","params":["400"]}},{"stallingLimit":6,"convergenceItem":{"action":"setDowntime","params":["500"]}}],"initialItems":[{"action":"setDowntime","params":["100"]}],"lastItems":[{"action":"setDowntime","params":["5000"]},{"action":"abort","params":[]}]}},{"id":{"uuid":"a7aeedb2-8d66-4e51-bb22-32595027ce71"},"maxMigrations":2,"autoConvergence":true,"migrationCompression":false,"enableGuestEvents":true,"name":"Post-copy migration","description":"The VM should not experience any significant downtime. If the VM migration is not converging for a long time, the migration will be switched to post-copy. The guest agent hook mechanism is enabled.","config":{"convergenceItems":[{"stallingLimit":1,"convergenceItem":{"action":"setDowntime","params":["150"]}},{"stallingLimit":2,"convergenceItem":{"action":"setDowntime","params":["200"]}}],"initialItems":[{"action":"setDowntime","params":["100"]}],"lastItems":[{"action":"postcopy","params":[]},{"action":"abort","params":[]}]}}] version: 4.1
DefaultCustomSerialNumber: Dummy serial number. version: general
HotPlugCpuSupported: {"x86":"false","ppc":"false"} version: 3.6
HotPlugCpuSupported: {"x86":"true","ppc":"false"} version: 4.0
HotPlugCpuSupported: {"x86":"true","ppc":"true"} version: 4.1
HotUnplugCpuSupported: {"x86":"false","ppc":"false"} version: 3.6
HotUnplugCpuSupported: {"x86":"false","ppc":"false"} version: 4.0
HotUnplugCpuSupported: {"x86":"true","ppc":"true"} version: 4.1
MaxNumOfTriesToRunFailedAutoStartVm: 10 version: general
RetryToRunAutoStartVmIntervalInSeconds: 30 version: general
DelayToRunAutoStartVmIntervalInSeconds: 10 version: general
MaxNumOfSkipsBeforeAutoStartVm: 3 version: general
CSRFProtection: false version: general
CORSSupport: false version: general
CORSAllowedOrigins:  version: general
PMHealthCheckEnabled: false version: general
PMHealthCheckIntervalInSec: 3600 version: general
FenceKdumpDestinationAddress:  version: general
FenceKdumpDestinationPort: 7410 version: general
FenceKdumpMessageInterval: 5 version: general
FenceKdumpListenerTimeout: 90 version: general
KdumpStartedTimeout: 30 version: general
CustomFenceAgentMapping:  version: general
CustomFenceAgentDefaultParams:  version: general
CustomFenceAgentDefaultParamsForPPC:  version: general
CustomVdsFenceOptionMapping:  version: general
CustomVdsFenceType:  version: general
CustomFencePowerWaitParam:  version: general
ClusterRequiredRngSourcesDefault:  version: 3.6
ClusterRequiredRngSourcesDefault:  version: 4.0
ClusterRequiredRngSourcesDefault:  version: 4.1
DefaultMTU: 1500 version: general
FenceStartStatusRetries: 18 version: general
FenceStartStatusDelayBetweenRetriesInSec: 10 version: general
FenceStopStatusRetries: 18 version: general
FenceStopStatusDelayBetweenRetriesInSec: 10 version: general
DefaultAutoConvergence: false version: general
DefaultMigrationCompression: false version: general
GlusterRefreshRateGeoRepStatusInSecs: 300 version: general
GlusterRefreshRateGeoRepDiscoveryInSecs: 3600 version: general
LibgfApiSupported: false version: 3.6
LibgfApiSupported: false version: 4.0
LibgfApiSupported: false version: 4.1
BackupCheckPeriodInHours: 6 version: general
BackupAlertPeriodInDays: 1 version: general
HostPackagesUpdateTimeInHours: 24 version: general
UserPackageNamesForCheckUpdate:  version: general
CertificationValidityCheckTimeInHours: 24 version: general
HostedEngineVmName: HostedEngine version: general
AutoImportHostedEngine: true version: general
AllowEditingHostedEngine: true version: general
HostedEngineConfigDiskSizeInBytes: 20480 version: general
AlertOnNumberOfLVs: 1000 version: general
HystrixMonitoringEnabled: false version: general
ImageProxyAddress: rhevm.example.com:54323 version: general
""".strip()


def test_engine_config_all_output():
    # Create output instance
    output = EngineConfigAll(context_wrap(ENGINE_CONFIG_ALL_OUTPUT))

    # Keyword with single value and version
    assert 'MaxStorageVdsTimeoutCheckSec' in output
    # import pdb; pdb.set_trace()
    assert output['MaxStorageVdsTimeoutCheckSec'] == ['30']
    assert output.get('MaxStorageVdsTimeoutCheckSec') == ['30']
    assert output.head('MaxStorageVdsTimeoutCheckSec') == '30'
    assert output.get_version('MaxStorageVdsTimeoutCheckSec') == ['general']

    # Keyword with mutiple values and versions
    assert output['HotUnplugCpuSupported'] == ['{"x86":"false","ppc":"false"}',
                                               '{"x86":"false","ppc":"false"}',
                                               '{"x86":"true","ppc":"true"}']
    assert output.last('HotUnplugCpuSupported') == '{"x86":"true","ppc":"true"}'  # noqa

    # Keyword with no value but version
    assert 'IPTablesConfigSiteCustom' in output
    assert output['IPTablesConfigSiteCustom'] == []
    assert output.get_version('IPTablesConfigSiteCustom') == ['general']

    # Keyword with no values but versions
    assert output['ClusterRequiredRngSourcesDefault'] == []
    assert output.get_version('ClusterRequiredRngSourcesDefault') == ['3.6',
                                                                      '4.0',
                                                                      '4.1']
    assert 'MigrationPolicies' in output
    assert output.get_version('MigrationPolicies') == ['3.6', '4.0', '4.1']

    # A keyword having multi-line output is not considered at-the-moment
    assert 'IPTablesConfig' not in output
    assert output['IPTablesConfig'] == []

    # Just another keyword
    assert 'UserSessionTimeOutInterval' in output
    assert output['UserSessionTimeOutInterval'] == ['30']
    assert output.get_version('UserSessionTimeOutInterval') == ['general']

    # A non existing keyword
    assert 'IDoNotExit' not in output
    assert output['IDoNotExit'] == []
    assert output.get('IDoNotExit') == []
    assert output.head('IDoNotExit') is None
    assert output.last('IDoNotExit') is None
    assert output.get_version('IDoNotExit') == []
