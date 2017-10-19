from .. import LogFileOutput, parser
from insights.specs import rhsm_log


@parser(rhsm_log)
class RhsmLog(LogFileOutput):
    """Class for parsing the log file: ``/var/log/rhsm/rhsm.log`` """
    pass
