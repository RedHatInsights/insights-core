from .. import LogFileOutput, mapper


@mapper('rhsm.log')
class RhsmLog(LogFileOutput):
    """Class for parsing the log file: ``/var/log/rhsm/rhsm.log`` """
    pass
