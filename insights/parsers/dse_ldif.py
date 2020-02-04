"""
DSELdifConfig - file ``/etc/dirsrv/slapd-<>/dse.ldif``
======================================================

This parser reads directory server's configuration
file ``dse.ldif``.  The ``DSELdifConfig`` class
implements the parsing and provides a ``list`` of all
configuration lines present in the file.

Sample configuration file::
# This is the RHDS configuration file. You should read the
# dse.ldif manual page in order to understand the options listed

dn:
objectClass: top
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
createTimestamp: 20151021124922Z
modifyTimestamp: 20151021124922Z

dn: cn=config
cn: config
objectClass: top
..

dn: cn=monitor
objectClass: top
objectClass: extensibleObject
cn: monitor
..

dn: cn=encryption,cn=config
objectClass: top
objectClass: nsEncryptionConfig
cn: encryption
..

dn: cn=features,cn=config
objectClass: top
objectClass: nsContainer
cn: features
numSubordinates: 5

dn: cn=replication,cn=config
objectClass: top
objectClass: extensibleobject
cn: replication
..

dn: cn=replSchema,cn=config
objectClass: top
objectClass: nsSchemaPolicy
cn: replSchema
..

dn: cn=uniqueid generator,cn=config
objectClass: top
objectClass: extensibleObject
nsState:: gK1YaqZe6gHTrx2O7V8kewAAAAAAAAAA
cn: uniqueid generator
..

Examples:
    >>> type(dse_ldif)
    <class 'insights.parsers.dse_ldif.DSELdifConfig'>
    >>> dse_ldif['creatorsName'] == ['cn=server,cn=plugins,cn=config']
    True
    >>> dse_ldif["numSubordinates"] == ['1']
    True
    >>> dse_ldif['modifyTimestamp'] == ['20151021124922Z']
    True
    >>> dse_ldif.last('numSubordinates') == '1'
    True
    >>> dse_ldif.last('numSubordinates2') == '1'
    False
    >>> dse_ldif.get_values('nsCertfile') == ['alias/slapd-rhds10-2-cert8.db']
    True
    >>> dse_ldif.get_values('WrongKeyNotPresent') == ['']
    True
    >>> dse_ldif.get_line('nsSSLClientAuth') == 'nsSSLClientAuth: allowed'
    True
    >>> next(iter(dse_ldif)).line == 'dn:'
    True
    >>> 'nsSSL3Ciphers' in dse_ldif
    True
    >>> dse_ldif['sslVersionMin'] == ['TLS1.0']
    True
    >>> dse_ldif.get('nsKeyfile')
    [KeyValue(keyword='nsKeyfile', value='alias/slapd-rhds10-2-key3.db', kw_lower='nskeyfile', line='nsKeyfile: alias/slapd-rhds10-2-key3.db')]
    >>> dse_ldif.line_uses_plus('nsTLS1')
    True
    >>> dse_ldif.line_uses_plus('nsTLS2')

"""
from collections import namedtuple
from .. import Parser, parser, get_active_lines
from insights.specs import Specs
import re

# Regex for matching 'Key:value' pairs seperated using :
PLUS_PATTERN = re.compile(r'(.*)\:(.*)')


@parser(Specs.dse_ldif)
class DSELdifConfig(Parser):
    """Parsing for ``/etc/dirsrv/slapd-<>/dse.ldif`` file.

    Properties:
        lines (list): List of `KeyValue` namedtupules for each line in
            the configuration file.
        keywords (set): Set of keywords present in the configuration
            file, each keyword has been converted to lowercase.
    """

    KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'kw_lower', 'line'])
    """namedtuple: Represent name value pair as a namedtuple with case ."""

    # Note about "+" options. In some rhds versions and for some keywords,
    # a "+" at the beginning of the value list signifies that the values are
    # added to the default list of values.
    # IT IS NOT DETECTED AND PARSED HERE.
    # `parse_content()` doesn't split the individual values because some
    # keywords don't have a list of values (just one string).
    # See the docstring in `line_uses_plus()` for more details.
    # Re: BZ#1697477
    # Config lines may also be delimited by `=`, and values may be quoted
    # with `"`. Here it is assumed that config lines are well-formed.
    def parse_content(self, content):
        self.lines = []
        for line in get_active_lines(content):
            line_splits = [s.strip() for s in re.split(r"[\s:]+", line, 1)]
            kw, val = line_splits[0], line_splits[1].strip('"') if \
                len(line_splits) == 2 else ''
            self.lines.append(self.KeyValue(
                kw, val, kw.lower(), line
            ))
        self.keywords = set([k.kw_lower for k in self.lines])

    def __contains__(self, keyword):
        """
        (bool) Is this keyword found in the configuration file?
        """
        return keyword.lower() in self.keywords

    def __iter__(self):
        """
        (iter) Yields a list of all the lines in the configuration file that
        actually contained a configuration option.
        """
        for line in self.lines:
            yield line

    def __getitem__(self, keyword):
        """
        (list) Get all values of this keyword.
        """
        kw = keyword.lower()
        if kw in self.keywords:
            return [kv.value for kv in self.lines if kv.kw_lower == kw]

    def get(self, keyword):
        """
        Get all declarations of this keyword in the configuration file.

        Returns:
            (list): a list of named tuples with the following properties:
                - ``keyword`` - the keyword as given on that line
                - ``value`` - the value of the keyword
                - ``kw_lower`` - the keyword converted to lower case
                - ``line`` - the complete line as found in the config file
        """
        kw = keyword.lower()
        return [kv for kv in self.lines if kv.kw_lower == kw]

    def get_values(self, keyword, default=''):
        """
        Get all the values assigned to this keyword.

        Firstly, if the keyword is not found in the configuration file, the
        value of the ``default`` option is used (defaulting to ``''``).

        """
        kw = keyword.lower()
        if kw in self.keywords:
            vals = [kv.value for kv in self.lines if kv.kw_lower == kw]
        else:
            vals = [default]
        return vals

    def get_line(self, keyword, default=''):
        """
        (str): Get the line with the last declarations of this keyword in the
        configuration file, optionally pretending that we had a line with the
        default value and a comment informing the user that this was a
        created default line.

        Parameters:
            keyword(str): Keyword to find
            default: optional value to supply if not found
        """
        lines = self.get(keyword)
        if lines:
            return lines[-1].line
        else:
            return "{keyword} {value}  # Implicit default".format(
                keyword=keyword, value=default
            )

    def line_uses_plus(self, keyword):
        lines = self.get(keyword)
        if lines:
            found_line = lines[-1].line
            match = PLUS_PATTERN.match(found_line)
            return bool(match)
        else:
            return None

    def last(self, keyword, default=None):
        """
        str: Returns the value of the last keyword found in config.

        Parameters:
            keyword(str): Keyword to find
            default: optional value to supply if not found
        """
        entries = self.__getitem__(keyword)
        if entries:
            return entries[-1]
