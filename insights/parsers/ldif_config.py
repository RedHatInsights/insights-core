"""
LDIF Configuration - file ``/etc/dirsrv/slapd-*/dse.ldif``
==========================================================

This module provides content of the directory server configuration from
the ``/etc/dirsrv/slapd-*/dse.ldif`` file.

Typical output of the ``/etc/dirsrv/slapd-*/dse.ldif`` file is::

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
    >>> ldif_config[3]['dn_name']
    'dn: cn=changelog5,cn=config'
    >>> ldif_config[3]['cn_name'][3]['modifiersName']
    'cn=Directory Manager'
    >>> ldif_config[3]['cn_name'][4]['modifyTimestamp']
    '20201026161228Z'
"""

from insights import Parser, parser
from insights.specs import Specs
from insights.parsers import SkipException
import re


@parser(Specs.ldif_config)
class LDIFParser(Parser, list):
    def parse_content(self, content):
        """
        Parse the LDIF data from the `/etc/dirsrv/slapd-*/dse.ldif` file.

        Attributes:
            data (list): List of lines in the file.

        Raises:
            SkipException: When nothing is parsered.
        """
        if not content:
            raise SkipException('The file is empty')
        m_flag = 0
        s_flag = 0

        for line in content:
            temp1 = {}
            if not line:
                continue
            elif line.startswith('dn:'):
                temp1['cn_name'] = []
                temp1['dn_name'] = line.strip(':')
                self.append(temp1)
                m_flag = m_flag + 1
                s_flag = 0
            elif re.search('.:\s', line):
                temp2 = {}
                temp2[line.split(':', 1)[0]] = line.split(':', 1)[1].split(' ', 1)[1]
                s_flag = s_flag + 1
            else:
                temp2 = {}
                key = list(self[m_flag - 1]['cn_name'][s_flag - 1].keys())[0]
                final_line = self[m_flag - 1]['cn_name'][s_flag - 1][key] + line.split(' ', 1)[1]

            if self and line.startswith('dn:'):
                continue
            elif self and re.search('.:\s', line):
                self[m_flag - 1]['cn_name'].append(temp2)
            else:
                key = list(self[m_flag - 1]['cn_name'][s_flag - 1].keys())[0]
                self[m_flag - 1]['cn_name'][s_flag - 1][key] = final_line
