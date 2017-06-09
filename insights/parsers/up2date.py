from .. import Parser, parser, get_active_lines, LegacyItemAccess


@parser('up2date')
class Up2Date(LegacyItemAccess, Parser):
    """Class to parse the ``up2date``

    Attributes:
        data (dict): A dict of up2date info which ignores comment lines.
        The first and second line for key word 'serverURL' will be ignored.

    For example:
        serverURL[comment]=Remote server URL
        #serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
        serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
    """
    def parse_content(self, content):
        up2date_info = {}
        for line in get_active_lines(content):
            if "[comment]" not in line and '=' in line:
                key, val = line.split('=')
                up2date_info[key.strip()] = val.strip()
        self.data = up2date_info
