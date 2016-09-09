from falafel.mappers.pluginconf_d import PluginConfD
from falafel.tests import context_wrap


PLUGIN = '''
[main]
enabled = 0
gpgcheck = 1
timeout = 120

# You can specify options per channel, e.g.:
#
#[rhel-i386-server-5]
#enabled = 1
#
#[some-unsigned-custom-channel]
#gpgcheck = 0
'''

PLUGINPATH = 'etc/yum/plugincon.d/rhnplugin.conf'


def test_pluginconf_d():
    plugin_info = PluginConfD.parse_context(context_wrap(PLUGIN, path=PLUGINPATH))

    assert plugin_info.data['main'] == {'enabled': '0',
                                        'gpgcheck': '1',
                                        'timeout': '120'}
    assert plugin_info.file_path == 'etc/yum/plugincon.d/rhnplugin.conf'
    assert plugin_info.file_name == 'rhnplugin.conf'
