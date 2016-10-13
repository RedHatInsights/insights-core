from .. import LogFileOutput, mapper


@mapper('engine.log')
class EngineLog(LogFileOutput):
    """
    ----------------- example of engine.log --------------------------
    2016-05-18 13:21:21,115 INFO [org.ovirt.engine.core.bll.scheduling.policyunits.EvenGuestDistributionBalancePolicyUnit] (DefaultQuartzScheduler_Worker-95) [5bc194fa] There is no host with more than 8 running guests, no balancing is needed
    2016-05-18 14:00:51,272 INFO [org.ovirt.engine.core.vdsbroker.VdsUpdateRunTimeInfo] (DefaultQuartzScheduler_Worker-95) [5bc194fa] VM ADLG8201 ab289661-bbaa-4d27-a67a-ad20626f60f0 moved from PoweringUp --> Paused
    2016-05-18 14:00:51,318 ERROR [org.ovirt.engine.core.dal.dbbroker.auditloghandling.AuditLogDirector] (DefaultQuartzScheduler_Worker-95) [5bc194fa] Correlation ID: null, Call Stack: null, Custom Event ID: -1, Message: VM ADLG8201 has paused due to storage I/O problem.
    ----------------- example of engine.log --------------------------
    """
    pass
