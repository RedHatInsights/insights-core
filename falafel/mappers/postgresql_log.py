from .. import LogFileOutput, mapper


@mapper('postgresql.log')
class PostgreSQLLog(LogFileOutput):
    pass
