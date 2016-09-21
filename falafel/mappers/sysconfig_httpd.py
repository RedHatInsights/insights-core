from .. import MapperOutput, mapper, get_active_lines


@mapper('sysconfig_httpd')
class HTTPDService(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        Returns a dict object contains all settings in /etc/sysconfig/httpd
        """
        result = {}
        for line in get_active_lines(content):
            if '=' in line:
                k, rest = line.split('=', 1)
                result[k.strip()] = rest.strip()
        return result
