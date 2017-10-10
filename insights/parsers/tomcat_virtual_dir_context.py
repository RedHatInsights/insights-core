"""
TomcatVirtualDirContext - command ``/bin/grep -R --include '*.xml' 'VirtualDirContext' /usr/share/tomcat*``
===========================================================================================================

This parser reads the output of ``/bin/grep -R --include '*.xml' 'VirtualDirContext' /usr/share/tomcat*``
and detects whether there are any config files which contain VirtualDirContext.

Sample input::

    /usr/share/tomcat/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"

Examples::

    >>> shared[TomcatVirtualDirContext].data
    {'/usr/share/tomcat/conf/server.xml':
     ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
     }
"""

from .. import Parser, parser
from . import ParseException, SkipException


@parser('tomcat_virtual_dir_context')
class TomcatVirtualDirContext(Parser):
    """
    Reports whether there is a VirtualDirContext option used in TomCat configuration file.
    """
    def __init__(self, *args, **kwargs):
        self.data = {}
        super(TomcatVirtualDirContext, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        if not content:
            raise SkipException('VirtualDirContext not used.')
        for line in content:
            if '/bin/grep: No such file or directory' in line:
                raise ParseException('grep command not found.')
            try:
                file_name, file_line = line.split(':', 1)  # Hoping that : is not part of the path
            except ValueError:
                raise ParseException('Unexpected grep output.')
            if file_name in self.data:
                self.data[file_name].append(file_line)
            else:
                self.data[file_name] = [file_line]
