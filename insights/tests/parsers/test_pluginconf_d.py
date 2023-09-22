import doctest

from insights.parsers import pluginconf_d
from insights.tests import context_wrap


PLUGIN = """
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
""".strip()

PLUGINPATH = '/etc/yum/plugincon.d/rhnplugin.conf'


def test_pluginconf_d_ini():
    plugin_info = pluginconf_d.PluginConfDIni(context_wrap(PLUGIN, path=PLUGINPATH))

    assert sorted(plugin_info.sections()) == sorted(['main', 'test'])
    assert 'main' in plugin_info
    assert plugin_info.get('main', 'gpgcheck') == '1'


def test_doc_examples():
    failed_count, tests = doctest.testmod(
        pluginconf_d,
        globs={'conf': pluginconf_d.PluginConfDIni(context_wrap(PLUGIN))}
    )
    assert failed_count == 0
