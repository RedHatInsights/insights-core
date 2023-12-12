"""
DseLDIF - file ``/etc/dirsrv/*/dse.ldif``
=========================================
"""

from collections import defaultdict

from insights import Parser, parser
from insights.core.exceptions import SkipComponent
from insights.core.filters import add_filter
from insights.specs import Specs

add_filter(Specs.dse_ldif, 'dn:')


@parser(Specs.dse_ldif)
class DseLDIF(Parser, list):
    """
    Parse the attributes out of the filtered lines of the
    ``/etc/dirsrv/*/dse.ldif`` file into a list of records. Each record will
    be stored as a defaultdict(list), take attribute name as the dict key, and
    wrap the attribute's values into a list as the dict value.

    The ``dse.ldif`` files are in the LDIF format (see ``man 5 ldif``). Due
    to the file content are filtered, there are some differences between the
    formal LDIF format and this parser.

    LDIF contains multi-row records where each record is identified by a
    ``dn:`` line ("dn" as in "distinguished name") and the record's other lines
    are attributes. Attributes may also have base64-encoded values, multiline
    values, and file-stored values.

    LDIF supports multiline values via continuing lines, one can break and
    continue a line or fold a line by indenting the continued portion of the
    line by one space.

    Since the content to be handled here is filtered content, the LDIF's
    continuing lines will be broken and no more trustable. When parsing, this
    parser will drop the lines startswith one space. This is acceptable for the
    current usage of the filter content. We can see to workaround this if
    continuing line requirement comes in the future.

    In the parsing process, line for ``dn:`` attribute will be recognized as
    the start of a record, the following lines will be included in this same
    record.

    Therefor, "dn:" is a default filter for the content collection. And a
    suggested way for filter adding is using the attribute key with ":" to
    minimize the collected data, eg. ``add_filter(Specs.dse_ldif, 'nsSSL3:')``.

    Sample input data::

        dn: cn=config
        nsslapd-return-default-opattr: namingContexts
        nsslapd-return-default-opattr: supportedControl
        nsslapd-securePort: 636
        nsslapd-security: on

        dn: cn=encryption,cn=config
        sslVersionMin: SSLv3
        sslVersionMax: TLS1.1
        nsSSL3: on

    Examples:
        >>> type(dse_ldif)
        <class 'insights.parsers.dse_ldif.DseLDIF'>
        >>> len(dse_ldif)
        2
        >>> dse_ldif[0]["nsslapd-return-default-opattr"]
        ['namingContexts', 'supportedControl']
        >>> dse_ldif[0]["nsslapd-security"]
        ['on']
        >>> "sslVersionMin" in dse_ldif[1]
        True
        >>> dse_ldif[1]["nsSSL3"][0]
        'on'

    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent('Empty file content')

        records = []
        attr_kval = defaultdict(list)
        for line in content:

            # empty lines or lines beginning with # are ignored
            if not line or line.startswith("#"):
                continue
            #  the continuing lines are ignored
            if line.startswith(" "):
                continue
            # lines not in attributes format are ignored
            if ":" not in line:
                continue

            attr_name, attr_value = [_.strip() for _ in line.split(':', 1)]
            if attr_name == 'dn':
                # line starts with 'dn:', taken as the start of a new record
                attr_kval = defaultdict(list)
                records.append(attr_kval)
                attr_kval[attr_name].append(attr_value)
            else:
                if attr_value.startswith(":"):
                    # base64-encrypted values not supported
                    continue
                if attr_value.startswith("<"):
                    # file-backed values not supported
                    continue
                attr_kval[attr_name].append(attr_value)

        for record in records:
            self.append(dict(record))

        if not self:
            raise SkipComponent("No valid content")
