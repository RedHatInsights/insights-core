from functools import partial
from insights.specs import Specs
from insights.core.context import SosArchiveContext
from insights.core.spec_factory import simple_file, first_of, glob_file

simple_file = partial(simple_file, context=SosArchiveContext)
glob_file = partial(glob_file, context=SosArchiveContext)


class SosSpecs(Specs):
    date = simple_file("sos_commands/general/date")
    ethtool = glob_file("sos_commands/networking/ethtool_*", ignore="ethtool_-.*")
    ethtool_S = glob_file("sos_commands/networking/ethtool_-S_*")
    ethtool_a = glob_file("sos_commands/networking/ethtool_-a_*")
    ethtool_c = glob_file("sos_commands/networking/ethtool_-c_*")
    ethtool_g = glob_file("sos_commands/networking/ethtool_-g_*")
    ethtool_i = glob_file("sos_commands/networking/ethtool_-i_*")
    ethtool_k = glob_file("sos_commands/networking/ethtool_-k_*")
    hostname = first_of([simple_file("sos_commands/general/hostname_-f"), simple_file("sos_commands/general/hostname")])
    installed_rpms = simple_file("installed-rpms")
    uname = simple_file("sos_commands/kernel/uname_-a")
    uptime = simple_file("sos_commands/general/uptime")
