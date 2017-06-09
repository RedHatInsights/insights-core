from .. import LogFileOutput, parser


@parser('postgresql.log')
class PostgreSQLLog(LogFileOutput):
    pass
