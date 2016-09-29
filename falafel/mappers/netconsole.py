from .. import get_active_lines, mapper, MapperOutput


@mapper('netconsole')
class NetConsole(MapperOutput):

    @staticmethod
    def parse_content(content):
        result = {}
        for line in get_active_lines(content):
            if '=' in line:
                k, v = line.split('=')
                result[k] = v
        return result
