from .. import LogFileOutput, mapper


@mapper('libvirtd.log')
def parse_libvirtd_log(context):
    return LogFileOutput(context.content, path=context.path)
