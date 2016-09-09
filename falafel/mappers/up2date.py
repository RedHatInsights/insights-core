from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines


@mapper('up2date')
class Up2Date(MapperOutput):

    @staticmethod
    def parse_content(content):
        '''
        Return a dict of up2date info which ignores comment lines.
        The first and second line for key word 'serverURL' will be ignored.
        For example:
        ~~~~
        serverURL[comment]=Remote server URL
        #serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
        serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
        ~~~~
        '''
        up2date_info = {}
        for line in get_active_lines(content):
            if "[comment]" not in line and '=' in line:
                key, val = line.split('=')
                up2date_info[key.strip()] = val.strip()
        return up2date_info
