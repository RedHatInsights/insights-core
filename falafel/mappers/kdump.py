import re
from falafel.core import computed, MapperOutput
from falafel.core.plugins import mapper
from falafel.mappers import chkconfig
from falafel.mappers.systemd import unitfiles


@mapper("cmdline")
def crashkernel_enabled(context):
    """
    Determine if kernel is configured to reserve memory for the crashkernel
    """

    for line in context.content:
        if 'crashkernel' in line:
            return True


@mapper("systemctl_list-unit-files")
@mapper("chkconfig")
def kdump_service_enabled(context):
    """
    Determine if kdump service is enabled with system

    RHEL5/6 uses chkconfig and if enabled will look something like this:
    kdump          	0:off	1:off	2:off	3:on	4:on	5:on	6:off

    RHEL7 uses systemctl list-unit-files and if enabled will look like this:
    kdump.service                               enabled
    """

    for line in context.content:
        if line.startswith('kdump') and (':on' in line or 'enabled' in line):
            return True


@mapper("kdump.conf")
class KDumpConf(MapperOutput):

    @staticmethod
    def parse_content(content):
        data = {}
        for line in content:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            k, v = line.split(' ', 1)
            data[k.strip()] = v.strip()
        return data

    @computed
    def using_local_disk(self):
        KDUMP_NETWORK_REGEX = re.compile(r'^\s*(ssh|nfs4?|net)\s+', re.I)
        KDUMP_LOCAL_DISK_REGEX = re.compile(r'^\s*(ext[234]|raw|xfs|btrfs|minix)\s+', re.I)
        local_disk = True
        for k in self.data.keys():
            if KDUMP_NETWORK_REGEX.search(k):
                local_disk = False
            elif KDUMP_LOCAL_DISK_REGEX.search(k):
                local_disk = True

        return local_disk


@mapper('kexec_crash_loaded')
class KexecCrashLoaded(MapperOutput):

    @staticmethod
    def parse_content(content):
        line = list(content)[0].strip()
        return line == '1'

    @computed
    def is_loaded(self):
        return self.data


def is_enabled(shared):
    chk = shared.get(chkconfig.ChkConfig)
    svc = shared.get(unitfiles.UnitFiles)
    if chk and chk.is_on('kdump'):
        return True

    return bool(svc and svc.is_on('kdump.service'))


@mapper("kdump.conf")
def kdump_using_local_disk(context):
    """
    Determine if kdump service is using local disk
    """

    KDUMP_NETWORK_REGEX = re.compile(r'^\s*(ssh|nfs4?|net)\s+', re.I)
    KDUMP_LOCAL_DISK_REGEX = re.compile(r'^\s*(ext[234]|raw|xfs|btrfs|minix)\s+', re.I)

    local_disk = True
    for line in context.content:
        if line.startswith('#') or line == '':
            continue
        elif KDUMP_NETWORK_REGEX.search(line):
            local_disk = False
        elif KDUMP_LOCAL_DISK_REGEX.search(line):
            local_disk = True

    return local_disk
