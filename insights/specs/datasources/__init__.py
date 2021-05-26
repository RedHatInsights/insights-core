import signal

from insights.combiners.cloud_provider import CloudProvider
from insights.combiners.ps import Ps
from insights.combiners.satellite_version import CapsuleVersion, SatelliteVersion
from insights.combiners.services import Services
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.lsmod import LsMod
from insights.parsers.mdstat import Mdstat


def get_running_commands(broker, commands):
    """
    Search for command in ``ps auxcww`` output and determine RPM providing binary

    Arguments:
        broker(dict): Current state of specs collected by Insights
        commands(str or list): Command or list of commands to search for in ps output

    Returns:
        list: List of the full command paths of the ``command``.

    Raises:
        Exception: Raises an exception if commands object is not a list or is empty
    """
    if not commands or not isinstance(commands, list):
        raise Exception('Commands argument must be a list object and contain at least one item')

    ps_list = [broker[Ps].search(COMMAND_NAME__contains=c) for c in commands]
    ps_cmds = [i for sub_l in ps_list for i in sub_l]
    ctx = broker[HostContext]

    ret = set()
    for cmd in set(p['COMMAND_NAME'] for p in ps_cmds):
        try:
            which = ctx.shell_out("/usr/bin/which {0}".format(cmd))
        except Exception:
            continue
        ret.add(which[0]) if which else None
    return sorted(ret)


def get_package(broker, command):
    """
    Arguments:
        broker(dict): Current state of specs collected by Insights
        command(str): The full command name to get the package

    Returns:
        str: The package that provides the ``command``.
    """
    ctx = broker[HostContext]
    resolved = ctx.shell_out("/usr/bin/readlink -e {0}".format(command))
    if resolved:
        pkg = ctx.shell_out("/usr/bin/rpm -qf {0}".format(resolved[0]), signum=signal.SIGTERM)
        if pkg:
            return pkg[0]
    raise SkipComponent


@datasource(CloudProvider, HostContext)
def is_aws(broker):
    """ bool: Returns True if this node is identified as running in AWS """
    cp = broker[CloudProvider]
    if cp and cp.cloud_provider == CloudProvider.AWS:
        return True
    raise SkipComponent()


@datasource(CloudProvider, HostContext)
def is_azure(broker):
    """ bool: Returns True if this node is identified as running in Azure """
    cp = broker[CloudProvider]
    if cp and cp.cloud_provider == CloudProvider.AZURE:
        return True
    raise SkipComponent()


@datasource(Ps, HostContext)
def is_ceph_monitor(broker):
    """ bool: Returns True if ceph monitor process ceph-mon is running on this node """
    ps = broker[Ps]
    if ps.search(COMMAND__contains='ceph-mon'):
        return True
    raise SkipComponent()


@datasource(HostContext)
def du_dirs_list(broker):
    """ Provide a list of directorys for the ``du_dirs`` spec to scan """
    return ['/var/lib/candlepin/activemq-artemis']


@datasource(CloudProvider, HostContext)
def is_gcp(broker):
    """ bool: Returns True if this node is identified as running in Google Cloud """
    cp = broker[CloudProvider]
    if cp and cp.cloud_provider == CloudProvider.GOOGLE:
        return True
    raise SkipComponent()


@datasource(Ps, HostContext)
def httpd_cmds(broker):
    """
    Function to search the output of ``ps auxcww`` to find all running Apache
    webserver processes and extract the binary path.

    Returns:
        list: List of the binary paths to each running process
    """
    return get_running_commands(broker, ['httpd', ])


@datasource(HostContext)
def md5chk_file_list(broker):
    """ Provide a list of files to be processed by the ``md5chk_files`` spec """
    return [
        "/etc/pki/product/69.pem", "/etc/pki/product-default/69.pem", "/usr/lib/libsoftokn3.so",
        "/usr/lib64/libsoftokn3.so", "/usr/lib/libfreeblpriv3.so", "/usr/lib64/libfreeblpriv3.so"
    ]


@datasource(Mdstat, HostContext)
def md_device_list(broker):
    md = broker[Mdstat]
    if md.components:
        return [dev["device_name"] for dev in md.components if dev["active"]]
    raise SkipComponent()


@datasource(Services, HostContext)
def is_pcp_enabled(broker):
    """ bool: Returns True if pmproxy service is on in services """
    if not broker[Services].is_on("pmproxy"):
        raise SkipComponent("pmproxy not enabled")


@datasource(SatelliteVersion, HostContext)
def is_satellite_server(broker):
    """
    bool: Returns True if the host is satellite server.
    """
    if broker[SatelliteVersion]:
        return True
    raise SkipComponent()


@datasource(CapsuleVersion, HostContext)
def is_satellite_capsule(broker):
    """
    bool: Returns True if the host is satellite capsule.
    """
    if broker[CapsuleVersion]:
        return True
    raise SkipComponent()


@datasource(LsMod, HostContext)
def is_mod_loaded_for_ss(broker):
    """
    bool: Returns True if the kernel modules required by ``ss -tupna``
    command are loaded.
    """
    lsmod = broker[LsMod]
    req_mods = ['inet_diag', 'tcp_diag', 'udp_diag']
    if all(mod in lsmod for mod in req_mods):
        return True
    raise SkipComponent()
