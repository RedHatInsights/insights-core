from .. import LogFileOutput, mapper


@mapper('libvirtd.log')
class LibVirtdLog(LogFileOutput):
    pass
