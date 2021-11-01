"""
LDIF Configuration - file ``/etc/dirsrv/slapd-*/dse.ldif``
==========================================================
"""

from insights import Parser, parser
from insights.specs import Specs
from insights.parsers import SkipException
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

    Sample output of the ``/etc/dirsrv/slapd-*/dse.ldif`` file::

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
        >>> ldif_config[3]['cn=changelog5,cn=config']['modifiersName']
        'cn=Directory Manager'
        >>> ldif_config[3]['cn=changelog5,cn=config']['modifyTimestamp']
        '20201026161228Z'
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('The file is empty')

        m_flag = 0
        for line in content:
            attr_kval = {}
            # line is emtpy
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
                    dn_kname = 'dn'
                    attr_kval[dn_kname] = {}
                    self.append(attr_kval)
                else:
                    dn_kname = line.split(':', 1)[1].split(' ', 1)[1]
                    attr_kval[dn_kname] = {}
                    self.append(attr_kval)
            # line starts with 'aci' attribute
            elif line.startswith('aci:'):
                if re.search('.:\s', line):
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
                aci_val = line.split(' ', 1)[1]
                aci_kline[0] = aci_kline[0] + aci_val
                continue
            # line is a non 'aci' attribute or file-backed value attribute
            elif re.search('.:\s', line) or re.search('.:<\s', line):
                attr_kval = {}
                attr_val = line.split(':', 1)[1].split(' ', 1)[1]
                attr_kval[line.split(':', 1)[0]] = attr_val
                attr_name = list(attr_kval.keys())[0]
            # line is a muti-line attribute lined for the non 'aci' attribute
            # line with a same attribute in mutiple line is ignored
            else:
                attr_kval = {}
                attr_kval[attr_name] = attr_val
                attr_kval[attr_name] = attr_val + line.split(' ', 1)[1]

            if self and line.startswith('dn:'):
                continue
            elif self and re.search('.:\s', line):
                if aci_key and aci_flag > 0:
                    self[m_flag - 1][dn_kname][aci_key] = aci_kline
                    aci_flag = 0
                self[m_flag - 1][dn_kname].update(attr_kval)
            else:
                self[m_flag - 1][dn_kname].update(attr_kval)
