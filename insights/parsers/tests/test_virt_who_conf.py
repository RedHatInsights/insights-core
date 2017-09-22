from insights.parsers.virt_who_conf import VirtWhoConf
from insights.tests import context_wrap

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
#reporter_id=
debug=False
oneshot=False
#log_per_config=False
#log_dir=
#log_file=
#configs=

[defaults]
owner=Satellite
env=Satellite
hypervisor_id=ID1
"""


def test_virt_who_conf():
    vwho_conf = VirtWhoConf(context_wrap(VWHO_CONF))
    assert vwho_conf.has_option('global', 'debug')
    assert vwho_conf.get('global', 'oneshot') == "False"
    assert vwho_conf.getboolean('global', 'oneshot') is False
    assert vwho_conf.get('global', 'interval') == "3600"
    assert vwho_conf.getint('global', 'interval') == 3600
    assert vwho_conf.items('defaults') == {
            'owner': 'Satellite',
            'env': 'Satellite',
            'hypervisor_id': 'ID1'}
