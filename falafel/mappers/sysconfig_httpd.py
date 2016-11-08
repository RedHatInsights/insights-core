from .. import Mapper, mapper, get_active_lines, LegacyItemAccess


@mapper('sysconfig_httpd')
class HTTPDService(LegacyItemAccess, Mapper):

    def parse_content(self, content):
        """
        Returns a dict object contains all settings in /etc/sysconfig/httpd
        """
        result = {}
        for line in get_active_lines(content):
            if '=' in line:
                k, rest = line.split('=', 1)
                result[k.strip()] = rest.strip()
        self.data = result
