from falafel.core.plugins import mapper
from falafel.mappers import get_active_lines


@mapper('up2date')
def up2date(context):
    '''
    Return a dict of up2date info which ignores comment lines.
    For example:
    ~~~~
    serverURL[comment]=Remote server URL
    #serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
    serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
    ~~~~
    The first and second line for key word 'serverURL' will be ignored.
    '''
    up2date_info = {}
    for line in get_active_lines(context.content):
        if "[comment]" not in line and '=' in line:
            key, val = line.split('=')
            up2date_info[key.strip()] = val.strip()
    return up2date_info
