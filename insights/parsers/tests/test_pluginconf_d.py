from insights.parsers.pluginconf_d import PluginConfD, PluginConfDIni
from insights.tests import context_wrap


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

[test]
test_multiline_config = http://example.com/repos/test/
                        http://mirror_example.com/repos/test/
'''

PLUGINPATH = '/etc/yum/plugincon.d/rhnplugin.conf'


def test_pluginconf_d():
    plugin_info = PluginConfD(context_wrap(PLUGIN, path=PLUGINPATH))

    assert plugin_info.data['main'] == {'enabled': '0',
                                        'gpgcheck': '1',
                                        'timeout': '120'}
    assert plugin_info.file_path == '/etc/yum/plugincon.d/rhnplugin.conf'
    assert plugin_info.file_name == 'rhnplugin.conf'

    assert plugin_info.data['test'] == {
        'test_multiline_config':
        'http://example.com/repos/test/,http://mirror_example.com/repos/test/'
    }

    # test iterator
    assert sorted(plugin_info) == sorted(['main', 'test'])


def test_pluginconf_d_ini():
    plugin_info = PluginConfDIni(context_wrap(PLUGIN, path=PLUGINPATH))

    assert sorted(plugin_info.sections()) == sorted(['main', 'test'])
    assert 'main' in plugin_info
    assert plugin_info.get('main', 'gpgcheck') == '1'
