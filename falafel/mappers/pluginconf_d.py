from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines


@mapper('pluginconf.d')
class PluginConfD(MapperOutput):

    @staticmethod
    def parse_content(content):
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
        return plugin_dict
