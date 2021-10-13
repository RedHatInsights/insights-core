"""
LDIF Configuration - file ``/etc/dirsrv/slapd-*/dse.ldif``
==========================================================

Parse the LDIF data from the `/etc/dirsrv/slapd-*/dse.ldif` file.

Examples:
    >>> ldif_config.data[1]['dn_name']
    'dn: cn=config'
    >>> ldif_config.data[1]['cn_name'][7]['modifiersName']
    'cn=directory manager'
    >>> ldif_config.data[1]['cn_name'][8]['modifyTimestamp']
    '20210609192548Z'
"""

from insights import Parser, parser
from insights.specs import Specs
from insights.parsers import SkipException
import re


@parser(Specs.ldif_config)
class LDIFParser(Parser):
    def parse_content(self, content):
        """Parse the LDIF data from the `/etc/dirsrv/slapd-*/dse.ldif` file."""
        if not content:
            raise SkipException('The file is empty')
        self.data = []
        m_flag = 0
        s_flag = 0

        for line in content:
            temp1 = {}
            if not line:
                continue
            elif line.startswith('dn:'):
                temp1['cn_name'] = []
                temp1['dn_name'] = line.strip(':')
                self.data.append(temp1)
                m_flag = m_flag + 1
                s_flag = 0
            elif re.search('.:\s', line):
                temp2 = {}
                temp2[line.split(':', 1)[0]] = line.split(':', 1)[1].split(' ', 1)[1]
                s_flag = s_flag + 1
            else:
                temp2 = {}
                key = list(self.data[m_flag - 1]['cn_name'][s_flag - 1].keys())[0]
                final_line = self.data[m_flag - 1]['cn_name'][s_flag - 1][key] + line.split(' ', 1)[1]

            if self.data and line.startswith('dn:'):
                continue
            elif self.data and re.search('.:\s', line):
                self.data[m_flag - 1]['cn_name'].append(temp2)
            else:
                key = list(self.data[m_flag - 1]['cn_name'][s_flag - 1].keys())[0]
                self.data[m_flag - 1]['cn_name'][s_flag - 1][key] = final_line
