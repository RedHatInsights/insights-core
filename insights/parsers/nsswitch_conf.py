"""
NSSwitchConf - file ``/etc/nsswitch.conf``
==========================================

"""

from insights import LegacyItemAccess, Parser, parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.nsswitch_conf)
class NSSwitchConf(Parser, LegacyItemAccess):
    """
    Read the contents of the ``/etc/nsswitch.conf`` file.

    Each non-commented line is split into the service and its sources.  The
    sources (e.g. 'files sss') are stored as is, as a string.

    nsswitch.conf is case insensitive.  This means that both the service and
    its sources are converted to lower case and searches should be done
    using lower case text.

    Attributes:
        data (dict): The service dictionary
        errors (list): Non-blank lines which don't contain a ':'
        sources (set): An unordered set of the sources seen in this file

    Sample content::

        # Example:
        #passwd:    db files nisplus nis
        #shadow:    db files nisplus nis
        #group:     db files nisplus nis

        passwd:     files sss
        shadow:     files sss
        group:      files sss
        #initgroups: files

        #hosts:     db files nisplus nis dns
        hosts:      files dns myhostname

    Examples:

        >>> nss = shared[NSSwitchConf]
        >>> 'passwd' in nss
        True
        >>> 'initgroups' in nss
        False
        >>> nss['passwd']
        'files nss'
        >>> 'files' in nss['hosts']
        True
        >>> nss.errors
        []
        >>> nss.sources
        set(['files', 'dns', 'sss', 'myhostname'])

    """
    def parse_content(self, content):
        self.errors = []
        self.data = {}
        self.sources = set()
        for line in get_active_lines(content):
            if ':' not in line:
                self.errors.append(line)
            else:
                service, sources = [s.lower().strip() for s in line.split(':', 1)]
                self.data[service] = sources
                self.sources.update(set(sources.split(None)))
