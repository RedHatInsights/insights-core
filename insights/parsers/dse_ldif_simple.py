# -*- coding: utf-8 -*-
"""
DseLdifSimple - file ``/etc/dirsrv/*/dse.ldif``
===============================================
"""


from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.dse_ldif)
class DseLdifSimple(Parser, dict):
    """
    Parse the attributes out of the filtered lines of the dse.ldif file into
    dict[attribute name] = attribute value.

    Please note the difference between the LDIF format and this parser.

    The file dse.ldif is in the LDIF format (see ``man 5 ldif``). LDIF contains
    multi-row records where each record is identified by a ``dn:`` line ("dn"
    as in "distinguished name") and the record's other lines are attributes.
    Attributes may also have base64-encoded values, multiline values, and
    file-stored values.

    The parser processes lines independently without tracking what the line is
    and which record it belongs to. Only plaintext single-line values are
    supported.

    This allows for filterable, efficient, and privacy-preserving processing of
    attributes whose names are valid only in a single distinguished name, and
    whose values are single-line plaintext only.

    Sample input data::

        dn: cn=config
        nsslapd-securePort: 636
        nsslapd-security: on

        dn: cn=encryption,cn=config
        sslVersionMin: SSLv3
        sslVersionMax: TLS1.1
        nsSSL3: on

    Examples:
        >>> type(dse_ldif_simple)
        <class 'insights.parsers.dse_ldif_simple.DseLdifSimple'>
        >>> dse_ldif_simple["nsslapd-security"]
        'on'
        >>> "sslVersionMin" in dse_ldif_simple
        True
        >>> dict(dse_ldif_simple)["nsSSL3"]
        'on'

    """

    def parse_content(self, content):
        data = {}
        for line in content:
            if line.startswith("#"):
                # lines beginning with # are ignored
                continue
            if ":" not in line:
                # only attribute: value lines supported
                continue
            if line.startswith(" "):
                # multi-line values not supported
                continue
            attr_name, attr_value = line.split(":", 1)
            if attr_value.startswith(":"):
                # base64-encrypted values not supported
                continue
            if attr_value.startswith("<"):
                # file-backed values not supported
                continue

            # Whitespace at either side of the value has no effect.
            attr_value = attr_value.strip()

            # If the same attribute is declared multiple times, the first
            # instance takes into effect, the rest is ignored by the 386
            # Directory Server.
            if attr_name not in data:
                data[attr_name] = attr_value
        self.update(data)
