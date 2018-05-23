from insights.combiners.virt_who_conf import AllVirtWhoConf
from insights.parsers.virt_who_conf import VirtWhoConf
from insights.parsers.sysconfig import VirtWhoSysconfig
from insights.tests import context_wrap

VWHO_D_CONF_ESX = """
## This is a template for virt-who configuration files. Please see
## virt-who-config(5) manual page for detailed information.
##
## virt-who checks all files in /etc/virt-who.d/ if they're valid ini-like
## files and uses them as configuration. Each file might contain more configs.
##
## You can uncomment and fill following template or create new file with
## similar content.

## For complete list of options, see virt-who-config(5) manual page.

## Terse version of the config template:
[esx_1]
type=esx
server=10.72.32.219
#encrypted_password=
owner=Satellite
env=Satellite
"""

VWHO_D_CONF_HYPER = """
## This is a template for virt-who configuration files. Please see
## virt-who-config(5) manual page for detailed information.
##
## virt-who checks all files in /etc/virt-who.d/ if they're valid ini-like
## files and uses them as configuration. Each file might contain more configs.
##
## You can uncomment and fill following template or create new file with
## similar content.

## For complete list of options, see virt-who-config(5) manual page.

## Terse version of the config template:
[hyperv_1]
type=hyperv
server=10.72.32.209
#encrypted_password=
owner=Satellite
env=Satellite
"""

VWHO_CONF = """
## This is a template for virt-who global configuration files. Please see
## virt-who-config(5) manual page for detailed information.
##
## virt-who checks /etc/virt-who.conf for sections 'global' and 'defaults'.
## The sections and their values are explained below.
## NOTE: These sections retain their special meaning and function only when present in /etc/virt-who.conf
##
## You can uncomment and fill following template or create new file with
## similar content.

#Terse version of the general config template:
[global]

interval=3600
debug=False
oneshot=False
#log_per_config=False
#log_dir=
#log_file=
#configs=

[defaults]
owner=Satellite
env=Satellite
"""

SYS_VIRTWHO = """
VIRTWHO_BACKGROUND=0
VIRTWHO_ONE_SHOT=1
VIRTWHO_INTERVAL=1000
VIRTWHO_SATELLITE6=1
""".strip()

SYS_VIRTWHO_SAT_LEGACY = """
VIRTWHO_BACKGROUND=1
VIRTWHO_SATELLITE=1
""".strip()

SYS_VIRTWHO_SAM = """
VIRTWHO_SAM=1
""".strip()

SYS_VIRTWHO_CP = """
VIRTWHO_SAM=0
""".strip()


def test_virt_who_conf_1():
    vw_sysconf = VirtWhoSysconfig(context_wrap(SYS_VIRTWHO))
    vwho_conf = VirtWhoConf(context_wrap(VWHO_CONF))
    vwhod_conf1 = VirtWhoConf(context_wrap(VWHO_D_CONF_HYPER))
    vwhod_conf2 = VirtWhoConf(context_wrap(VWHO_D_CONF_ESX))
    result = AllVirtWhoConf(vw_sysconf, [vwho_conf, vwhod_conf1, vwhod_conf2])
    assert result.background is False
    assert result.oneshot is True
    assert result.interval == 1000
    assert result.sm_type == 'sat6'
    assert sorted(result.hypervisor_types) == sorted(['esx', 'hyperv'])

    expected = [{'name': 'esx_1', 'server': '10.72.32.219', 'env': 'Satellite',
                 'owner': 'Satellite', 'type': 'esx'},
                {'name': 'hyperv_1', 'server': '10.72.32.209', 'env': 'Satellite',
                 'owner': 'Satellite', 'type': 'hyperv'}]
    for d in result.hypervisors:
        assert d in expected


def test_virt_who_conf_2():
    vw_sysconf = VirtWhoSysconfig(context_wrap(SYS_VIRTWHO_SAT_LEGACY))
    vwho_conf = VirtWhoConf(context_wrap(VWHO_CONF))
    result = AllVirtWhoConf(vw_sysconf, [vwho_conf])
    assert result.background is True
    assert result.oneshot is False
    assert result.interval == 3600
    assert result.sm_type == 'sat5'


def test_virt_who_conf_3():
    vw_sysconf = VirtWhoSysconfig(context_wrap(SYS_VIRTWHO_SAM))
    vwho_conf = VirtWhoConf(context_wrap(VWHO_CONF))
    result = AllVirtWhoConf(vw_sysconf, [vwho_conf])
    assert result.sm_type == 'sam'


def test_virt_who_conf_4():
    vw_sysconf = VirtWhoSysconfig(context_wrap(SYS_VIRTWHO_CP))
    vwho_conf = VirtWhoConf(context_wrap(VWHO_CONF))
    result = AllVirtWhoConf(vw_sysconf, [vwho_conf])
    assert result.sm_type == 'cp'
