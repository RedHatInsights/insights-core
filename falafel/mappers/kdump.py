import re
from urlparse import urlparse
from ..mappers import chkconfig, ParseException
from ..mappers.systemd import unitfiles
from .. import Mapper, mapper, SysconfigOptions


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
class KDumpConf(Mapper):
    """
    A dictionary like object for the values of the kdump.conf file.

    Attributes:
    lines: dictionary of line numbers and raw lines from the file
    comments: list of comment lines
    inline_comments: list of lines containing inline comments
    """
    NET_COMMANDS = set(['nfs', 'net', 'ssh'])

    def parse_content(self, content):
        self.data = {}
        lines = {}
        items = {'options': {}}
        comments = []
        inline_comments = []

        for i, _line in enumerate(content):
            lines[i] = _line
            line = _line.strip()
            if not line:
                continue
            if line.startswith('#'):
                comments.append(_line)
                continue
            r = line.split('=', 1)
            if len(r) == 1 or len(r[0].split()) > 1:
                r = line.split(None, 1)
                if len(r) == 1:
                    raise ParseException('Cannot split %s', line)
            k, v = r
            k = k.strip()
            parts = v.strip().split('#', 1)
            v = parts[0].strip()

            opt_kw = 'options'
            if k != opt_kw:
                items[k] = v
            else:
                mod, rest = v.split(None, 1)
                items[opt_kw][mod] = rest.strip()

            if len(parts) > 1:
                inline_comments.append(_line)

        self.data['lines'] = lines
        self.data['items'] = items
        self.data['comments'] = comments
        self.data['inline_comments'] = inline_comments

    def options(self, module):
        return self.get('options', {}).get(module, '')

    def _network_lines(self, net_commands=NET_COMMANDS):
        return filter(None, [self.get(n) for n in net_commands])

    def get_ip(self, net_commands=NET_COMMANDS):
        ip_re = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
        for l in self._network_lines(net_commands):
            matched_ip = ip_re.search(l)
            if matched_ip:
                return matched_ip.group()

    def is_ssh(self):
        return 'ssh' in self or '@' in self.get('net', '')

    def is_nfs(self):
        return 'nfs' in self or '@' not in self.get('net', '')

    def get_hostname(self, net_commands=NET_COMMANDS):
        for l in self._network_lines(net_commands):
            # required for urlparse to interpret as host instead of
            # relative path
            if '//' not in l:
                l = '//' + l
            netloc = urlparse(l).netloc

            # strip user:pass@
            i = netloc.find('@')
            if i != -1:
                netloc = netloc[i + 1:]

            # strip port
            return netloc.rsplit(':', 1)[0]

    @property
    def ip(self):
        return self.get_ip()

    @property
    def hostname(self):
        return self.get_hostname()

    @property
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

    @property
    def comments(self):
        return self.data.get('comments')

    @property
    def inline_comments(self):
        return self.data.get('inline_comments')

    @property
    def lines(self):
        return self.data['lines']

    def __getitem__(self, key):
        if isinstance(key, int):
            raise TypeError("Mapper does not support integer indexes")
        return self.data['items'][key]

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.data['items']


@mapper('kexec_crash_loaded')
class KexecCrashLoaded(Mapper):

    def parse_content(self, content):
        line = list(content)[0].strip()
        self.is_loaded = line == '1'


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


@mapper('kdump')
class SysconfigKdump(SysconfigOptions):
    """
    Read data from the ``/etc/sysconfig/kdump`` file.

    This sets the following properties for ease of access:

    * KDUMP_COMMANDLINE
    * KDUMP_COMMANDLINE_REMOVE
    * KDUMP_COMMANDLINE_APPEND
    * KDUMP_KERNELVER
    * KDUMP_IMG
    * KDUMP_IMG_EXT
    * KEXEC_ARGS

    These are set to the value of the named variable in the kdump sysconfig
    file, or '' if not found.
    """

    KDUMP_KEYS = [
        'KDUMP_COMMANDLINE',
        'KDUMP_COMMANDLINE_REMOVE',
        'KDUMP_COMMANDLINE_APPEND',
        'KDUMP_KERNELVER',
        'KDUMP_IMG',
        'KDUMP_IMG_EXT',
        'KEXEC_ARGS',
    ]

    def parse_content(self, content):
        super(SysconfigKdump, self).parse_content(content)
        for key in self.KDUMP_KEYS:
            setattr(self, key, self.data.get(key, ''))


@mapper('kexec_crash_size')
class KexecCrashSize(Mapper):
    """
    Parses the `/sys/kernel/kexec_crash_size` file which tells the
    reserved memory size for the crash kernel.

    Attributes
    ----------
    size (int): reserved memory size for the crash kernel
    """

    def parse_content(self, content):
        size = list(content)[0].strip()
        if size.isdigit():
            self.size = int(size)
        else:
            self.size = 0
