from .. import Mapper, LogFileOutput, mapper


@mapper('sysctl')
class Sysctl(Mapper):

    def parse_content(self, content):
        r = {}
        for line in content:
            if "=" not in line:
                continue

            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            r[k] = v
        self.data = r


@mapper("sysctl.conf_initramfs")
class SysctlConfInitramfs(LogFileOutput):
    """Shared mapper for the output of ``lsinitrd`` applied to kdump
    initramfs images to view ``sysctl.conf`` and ``sysctl.d``
    configurations.

    For now, the file is treated as raw lines (as a ``LogFileOutput``
    mapper.  This is because the output of the command, applied to
    multiple files to examine multiple files does not seem to be
    unambiguously parsible.

    Since the only plugins requireing the file to date "grep out"
    certain strings, this approach will suffice.
    """
    pass


@mapper('sysctl')
def runtime(context):
    """Deprecated, do not use."""
    return Sysctl(context).data
