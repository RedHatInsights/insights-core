"""
EngineLog - file ``var/log/ovirt-engine/engine.log``
====================================================

This is a standard log parser based on the LogFileOutput class.

Sample input::

    2016-05-18 13:21:21,115 INFO [org.ovirt.engine.core.bll.scheduling.policyunits.EvenGuestDistributionBalancePolicyUnit] (DefaultQuartzScheduler_Worker-95) [5bc194fa] There is no host with more than 8 running guests, no balancing is needed
    2016-05-18 14:00:51,272 INFO [org.ovirt.engine.core.vdsbroker.VdsUpdateRunTimeInfo] (DefaultQuartzScheduler_Worker-95) [5bc194fa] VM ADLG8201 ab289661-bbaa-4d27-a67a-ad20626f60f0 moved from PoweringUp --> Paused
    2016-05-18 14:00:51,318 ERROR [org.ovirt.engine.core.dal.dbbroker.auditloghandling.AuditLogDirector] (DefaultQuartzScheduler_Worker-95) [5bc194fa] Correlation ID: null, Call Stack: null, Custom Event ID: -1, Message: VM ADLG8201 has paused due to storage I/O problem.

Examples:

    >>> logs = shared[EngineLog]
    >>> 'has paused due to storage I/O problem' in logs
    True
    >>> logs.get('INFO')
    ['2016-05-18 13:21:21,115 INFO [org.ovirt.engine.core.bll.scheduling.policyunits.EvenGuestDistributionBalancePolicyUnit] (DefaultQuartzScheduler_Worker-95) [5bc194fa] There is no host with more than 8 running guests, no balancing is needed',
     '2016-05-18 14:00:51,272 INFO [org.ovirt.engine.core.vdsbroker.VdsUpdateRunTimeInfo] (DefaultQuartzScheduler_Worker-95) [5bc194fa] VM ADLG8201 ab289661-bbaa-4d27-a67a-ad20626f60f0 moved from PoweringUp --> Paused']
    >>> from datetime import datetime
    >>> list(logs.get_after(datetime(2016, 5, 18, 14, 0, 0)))
    ['2016-05-18 14:00:51,272 INFO [org.ovirt.engine.core.vdsbroker.VdsUpdateRunTimeInfo] (DefaultQuartzScheduler_Worker-95) [5bc194fa] VM ADLG8201 ab289661-bbaa-4d27-a67a-ad20626f60f0 moved from PoweringUp --> Paused',
     '2016-05-18 14:00:51,318 ERROR [org.ovirt.engine.core.dal.dbbroker.auditloghandling.AuditLogDirector] (DefaultQuartzScheduler_Worker-95) [5bc194fa] Correlation ID: null, Call Stack: null, Custom Event ID: -1, Message: VM ADLG8201 has paused due to storage I/O problem.']

"""
from insights.util import deprecated
from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.engine_log)
class EngineLog(LogFileOutput):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.ovirt_engine_log.EngineLog` instead.

    Provide access to ovirt engine logs using the LogFileOutput parser class.
    """
    def __init__(self, *args, **kwargs):
        deprecated(EngineLog, "Import EngineLog from insights.parsers.ovirt_engine_log instead")
        super(EngineLog, self).__init__(*args, **kwargs)
