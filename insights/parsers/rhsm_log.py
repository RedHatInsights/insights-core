from .. import LogFileOutput, parser


@parser('rhsm.log')
class RhsmLog(LogFileOutput):
    """Class for parsing the log file: ``/var/log/rhsm/rhsm.log`` """
    pass
