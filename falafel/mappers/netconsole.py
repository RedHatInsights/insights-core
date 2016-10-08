from .. import get_active_lines, mapper, Mapper, LegacyItemAccess


@mapper('netconsole')
class NetConsole(LegacyItemAccess, Mapper):

    def parse_content(self, content):
        result = {}
        for line in get_active_lines(content):
            if '=' in line:
                k, v = line.split('=')
                result[k] = v
        self.data = result
