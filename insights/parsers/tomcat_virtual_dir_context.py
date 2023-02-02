"""
Parsers for usage of VirtualDirContext option in Tomcat config files
====================================================================

This module provides the following parsers:

TomcatVirtualDirContextFallback
-------------------------------

This is a parser for a command for finding config files in default location:

``/usr/bin/find /usr/share -maxdepth 1 -name 'tomcat*' -exec grep -R -s 'VirtualDirContext' --include '*.xml' '{}' +``

It is especially useful if the Tomcat server is not running.


TomcatVirtualDirContextTargeted
-------------------------------

This is a parser for a command for finding config files in the custom location defined in a command
line:

``/bin/grep -R -s 'VirtualDirContext' --include '*.xml' {catalina}``

Where ``catalina`` variable is computed as following:

``/bin/ps auxww | awk '/java/ { match($0, "\\-Dcatalina\\.home=([^[:space:]]+)", a); match($0, "\\-Dcatalina\\.base=([^[:space:]]+)", b); if (a[1] != "" || b[1] != "") print a[1] " " b[1] }'``


Both parsers detect whether there are any config files which contain VirtualDirContext.

Sample input::

    /usr/share/tomcat/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"

Examples::

    >>> shared[TomcatVirtualDirContextFallback].data
    {'/usr/share/tomcat/conf/server.xml':
     ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
     }
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


class TomcatVirtualDirContextBase(CommandParser):
    """
    Generic parser which finds whether there is a VirtualDirContext option used in TomCat
    configuration file.
    """
    def __init__(self, *args, **kwargs):
        self.data = {}
        super(TomcatVirtualDirContextBase, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        for line in content:
            try:
                file_name, file_line = line.split(':', 1)  # Hoping that : is not part of the path
            except ValueError:
                continue  # skip this line
            if file_name.endswith('.xml'):  # Make sure that nothing else is stored
                if file_name in self.data:
                    self.data[file_name].append(file_line)
                else:
                    self.data[file_name] = [file_line]

        if self.data == {}:
            raise SkipComponent('VirtualDirContext not used.')


@parser(Specs.tomcat_vdc_fallback)
class TomcatVirtualDirContextFallback(TomcatVirtualDirContextBase):
    """
    Reports whether there is a VirtualDirContext option used in TomCat configuration file. Looks
    for the configuration files in default location.
    """
    pass


@parser(Specs.tomcat_vdc_targeted)
class TomcatVirtualDirContextTargeted(TomcatVirtualDirContextBase):
    """
    Reports whether there is a VirtualDirContext option used in TomCat configuration file. Looks
    for the configuration files in location derived from running Tomcat command.
    """
    pass
