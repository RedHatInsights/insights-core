"""
TomcatVirtualDirContextCombined - check VirtualDirContext option used in Tomcat
===============================================================================

This combiner provides information about whether a VirtualDirContext is used in config files in
both default locations or location derived from running Tomcat process.

Examples::

    >>> shared[TomcatVirtualDirContextCombined].data
    {'/usr/share/tomcat/conf/server.xml':
     ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
     }
"""
from ..core.plugins import combiner
from ..parsers.tomcat_virtual_dir_context import TomcatVirtualDirContextFallback, \
    TomcatVirtualDirContextTargeted


@combiner([TomcatVirtualDirContextFallback, TomcatVirtualDirContextTargeted])
class TomcatVirtualDirContextCombined(object):
    """
    Combiner for VirtualDirContext usage in Tomcat config files.
    """
    def __init__(self, tomcat_vdc_fallback, tomcat_vdc_targeted):
        self.data = {}
        fallback = tomcat_vdc_fallback if tomcat_vdc_fallback else None  # Returns one parser
        targeted = tomcat_vdc_targeted if tomcat_vdc_targeted else []  # Returns list of parsers
        for parser in [fallback] + targeted:
            if parser:
                for key in parser.data:
                    if key not in self.data:
                        self.data[key] = []
                    self.data[key] += parser.data[key]

        # Deduplicate lines
        for key, value in self.data.items():
            self.data[key] = sorted(set(value))
