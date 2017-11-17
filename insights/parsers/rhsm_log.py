from .. import LogFileOutput, parser
from insights.specs import rhsm_log


@parser(rhsm_log)
class RhsmLog(LogFileOutput):
    """
    Class for parsing the log file: ``/var/log/rhsm/rhsm.log``.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """

    pass
