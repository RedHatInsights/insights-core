from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines


class HTTPDService(MapperOutput):
    pass


@mapper('httpd')
def httpd_service_conf(context):
    """
    Returns all settings in /etc/sysconfig/httpd
    """
    result = {}
    for line in get_active_lines(context.content):
        if '=' in line:
            k, rest = line.split('=', 1)
            result[k.strip()] = rest.strip()
    if result:  # i.e. if we got any lines parsed successfully
        return HTTPDService(result)
