from .. import LogFileOutput, mapper


@mapper('catalina.out')
class CatalinaOut(LogFileOutput):
    pass
