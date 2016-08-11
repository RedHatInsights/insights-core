from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines


class PluginConfD(MapperOutput):
    pass


@mapper('pluginconf.d')
def pluginconf_d(context):
    '''
    Return a object contains a dit.
    There are several files in 'pluginconf.d' directory, which have the same format.
    -----------one of the files : rhnplugin.conf
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
    ------------------------------------------------
    The output will looks like:
    {
        "main": {
            "gpgcheck": "1",
            "enabled": "0",
            "timeout": "120"
        }
    }
    '''
    plugin_info = {}
    section = None
    info = {}

    for line in get_active_lines(context.content):
        if section:
            if line.startswith('['):
                plugin_info[section] = info
                section = line[1:-1]
                info = {}
                continue
            else:
                key, val = line.split("=", 1)
                info[key.strip()] = val.strip()
        else:
            section = line[1:-1]
    if section:
        plugin_info[section] = info
    return PluginConfD(plugin_info, path=context.path)
