from falafel.core.plugins import mapper
from falafel.core import LogFileOutput


@mapper('libvirtd.log')
def parse_libvirtd_log(context):
    return LogFileOutput(context.content, path=context.path)
