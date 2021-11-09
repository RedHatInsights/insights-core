"""
LDIF Configuration - file ``/etc/dirsrv/slapd-*/dse.ldif``
==========================================================
"""

from insights import Parser, parser
from insights.specs import Specs
from insights.parsers import SkipException, keyword_search
import re


@parser(Specs.ldif_config)
class LDIFParser(Parser, list):
    """
    Parse the content of the directory server configuration from
    the ``/etc/dirsrv/slapd-*/dse.ldif`` file.

    The file dse.ldif is in the LDIF format. LDIF contains multi-row records
    where each record is identified by a ``dn:`` line ("dn" as in "distinguished
    name") and the record's other lines are attributes. The value may be specified
    as UTF-8 text or as base64 encoded data, or a URI may be provided to the
    location of the attribute value.

    Attributes:

    list: A list of dictionaries for each 'dn' attribute block of the ldif configuration::

    Sample output of the 'cn=changelog5,cn=config' dn attribute block of the
    ``/etc/dirsrv/slapd-*/dse.ldif`` file::

        dn: cn=changelog5,cn=config
        cn: changelog5
        createTimestamp: 20201026161228Z
        creatorsName: cn=Directory Manager
        modifiersName: cn=Directory Manager
        modifyTimestamp: 20201026161228Z
        nsslapd-changelogdir: /var/lib/dirsrv/slapd-IDM-NYPD-FINEST/cldb
        nsslapd-changelogmaxage: 7d
        objectClass: top
        objectClass: extensibleobject

    Examples:
        >>> ldif_config = sorted(ldif_config, key=lambda x: x['dn'])
        >>> ldif_config[1]['dn']
        'cn=changelog5,cn=config'
        >>> ldif_config[1]['modifiersName']
        'cn=Directory Manager'
        >>> ldif_config[1]['modifyTimestamp']
        '20201026161228Z'
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('The file is empty')

        m_flag = 0
        for line in content:
            attr_kval = {}
            line = line.strip()
            if not line:
                continue
            elif line.startswith('#'):
                # lines beginning with # are ignored
                continue
            # line starts with 'dn' attribute
            elif line.startswith('dn:'):
                aci_kline = []
                aci_flag = 0
                m_flag += 1
                # line starts with 'dn' attribute line
                if line == 'dn:':
                    attr_kval[line.split(':', 1)[0]] = line.split(':', 1)[1]
                    self.append(attr_kval)
                else:
                    attr_kval[line.split(':', 1)[0].split(' ', 1)[0]] = line.split(':', 1)[1].split(' ', 1)[1]
                    self.append(attr_kval)
            # line starts with 'aci' attribute
            elif line.startswith('aci:'):
                aci_val = line.split(':', 1)[1].split(' ', 1)[1]
                aci_key = line.split(':', 1)[0].split(' ', 1)[0]
                if len(aci_kline) == 0:
                    aci_kline.append(aci_val)
                else:
                    aci_kline[0] = aci_kline[0] + aci_val
                aci_flag += 1
                continue
            # line is a muti-line value with the 'aci' attribute
            elif (not re.search('.:\s', line) and aci_flag > 0):
                aci_kline[0] = aci_kline[0] + line
                continue
            # line is a non 'aci' attribute or file-backed value attribute
            elif re.search('.:\s', line) or re.search('.:<\s', line):
                attr_kval = {}
                attr_val = line.split(':', 1)[1].split(' ', 1)[1]
                attr_kval[line.split(':', 1)[0]] = attr_val
                attr_name = list(attr_kval.keys())[0]
            # line is a muti-line attribute lined for the non 'aci' attribute
            # line with the same attribute in multiple lines is ignored
            else:
                attr_kval = {}
                attr_kval[attr_name] = attr_val
                attr_kval[attr_name] = attr_val + line

            if self and line.startswith('dn:'):
                continue
            elif self and re.search('.:\s', line):
                if aci_key and aci_flag > 0:
                    self[m_flag - 1][aci_key] = aci_kline[0]
                    aci_flag = 0
                self[m_flag - 1].update(attr_kval)
            else:
                self[m_flag - 1].update(attr_kval)

    def search(self, **kwargs):
        """
        Get the list for the 'dn' attribute block by searching the ldif configuration.
        This uses the :py:func:`insights.parsers.keyword_search` function for searching,
        see its documentation for usage details. If no search parameters are given or does
        match the search, then nothing will be returned.

        Returns:
            list: A list of dictionaries for each 'dn' attribute block of the ldif configuration that match the given
            search criteria.

        Examples:
            >>> sorted(ldif_config.search(dn='cn=features,cn=config'))
            [{'dn': 'cn=features,cn=config', 'objectClass': 'nsContainer', 'numSubordinates': '5', 'cn': 'features'}]
            >>> sorted(ldif_config.search(dn='cn=sasl,cn=config'))
            [{'dn': 'cn=sasl,cn=config', 'cn': 'sasl', 'objectClass': 'nsContainer', 'numSubordinates': '1'}]
            >>> sorted(ldif_config.search(cn='features'))
            [{'dn': 'cn=features,cn=config', 'objectClass': 'nsContainer', 'numSubordinates': '5', 'cn': 'features'}]
        """
        return keyword_search(self, **kwargs)
