"""
namei -monl ... - Command
=========================

The ``namei -monl ...`` command shows the mode bits, owner and group
information for each file/directory/device-node of below paths:
/usr/share/tomcat/work/Catalina/localhost/candlepin/tmp
/var/cache/tomcat/work/Catalina/localhost/candlepin

Sample input is shown in the Examples.

Examples:
    >>> NAMEI_TOMCAT = '''
    f: /usr/share/tomcat/work/Catalina/localhost/candlepin
    dr-xr-xr-x root   root   /
    drwxr-xr-x root   root   usr
    drwxr-xr-x root   root   share
    drwxrwxr-x root   tomcat tomcat
    lrwxrwxrwx root   tomcat work -> /var/cache/tomcat/work
    drwxr-xr-x tomcat tomcat Catalina
    drwxr-xr-x tomcat tomcat localhost
    drwxr-xr-x tomcat tomcat candlepin
    f: /var/cache/tomcat/work/Catalina/localhost/candlepin
    dr-xr-xr-x root   root   /
    drwxr-xr-x root   root   var
    drwxr-xr-x root   root   cache
    drwxrwx--- root   tomcat tomcat
    drwxrwx--- root   tomcat work
    drwxr-xr-x tomcat tomcat Catalina
    drwxr-xr-x tomcat tomcat localhost
    drwxr-xr-x tomcat tomcat candlepin
    '''
    >>> from falafel.tests import context_wrap
    >>> namei_tomcat = NameiTomcat(context_wrap(NAMEI_TOMCAT))
    <__main__.NameiTomcat object at 0x7f674914c690>
    >>> namei_tomcat.paths
    ["/var/cache/tomcat/work/Catalina/localhost/candlepin",
     "/usr/share/tomcat/work/Catalina/localhost/candlepin"]
    >>> "/var/cache" in namei_tomcat
    True
    >>> "Catalina" in namei_tomcat
    False
    >>> namei_tomcat.get("/var/cache/tomcat")
    <falafel.mappers.namei_tomcat.Namei object at 0x7f8eba9f4810>
    >>> namei_tomcat.get("/var/cache/tomcat/work/").owner
    'root'
    >>> namei_tomcat.get("/var/cache/tomcat/work").link
    '/var/cache/tomcat/work'
    >>> namei_tomcat.get("/var/cache/tomcat/work/Catalina").group
    'tomcat'
"""
from .. import mapper, Mapper


class Namei(object):
    """Class for holding the namei information of each file/directory/device-node
    in the ``pathname``.

    Attributes:
        mode (string): 'drwxr-xr-x'
        owner (string): 'root'
        group (string): 'tomcat'
        link (None or string): '/var/cache/tomcat/work'
    """
    def __init__(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)


@mapper("namei_tomcat")
class NameiTomcat(Mapper):
    """Class for parsing the output of ``namei -monl ...`` command running on
    tomcat's essential paths.

    Attributes:
        paths (list of string): List of all ``pathname`` that the command outputs.

    """
    def __contains__(self, item):
        item = item[:-2] if item[-1] == '/' else item
        return item in self.data

    def __getitem__(self, item):
        item = item[:-1] if item[-1] == '/' else item
        return self.data[item]

    def get(self, item):
        item = item[:-1] if item[-1] == '/' else item
        return self.data.get(item)

    def __iter__(self):
        for k, v in self.data.items():
            yield k, v

    def parse_content(self, content):
        self.data = {}
        self.paths = []
        pathname = None
        for line in content:
            if line.startswith('f:'):
                self.paths.append(line.split()[-1])
                pathname = ''
            else:
                line_sp = line.split(None, 3)
                path = {}
                path['mode'] = line_sp[0]
                path['owner'] = line_sp[1]
                path['group'] = line_sp[2]
                sp_3 = line_sp[3].split()
                path['link'] = sp_3[-1] if len(sp_3) > 1 else None
                pathname = (pathname + '/' + sp_3[0]).replace('//', '/')
                self.data[pathname] = Namei(path)
