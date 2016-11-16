from .. import Mapper, mapper, get_active_lines, LegacyItemAccess


@mapper('pluginconf.d')
class PluginConfD(LegacyItemAccess, Mapper):
    '''
    Return an object contains a dict.
    {
        "main": {
            "gpgcheck": "1",
            "enabled": "0",
            "timeout": "120"
        }
    }
    ------------------------------------------------
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
    '''

    def parse_content(self, content):
        plugin_dict = {}
        section_dict = {}
        key = None
        for line in get_active_lines(content):
            if line.startswith('['):
                section_dict = {}
                plugin_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, _, value = line.partition("=")
                key = key.strip()
                section_dict[key] = value.strip()
            else:
                if key:
                    section_dict[key] = ','.join([section_dict.get(key), line])
        self.data = plugin_dict

    def __iter__(self):
        for sec in self.data:
            yield sec
