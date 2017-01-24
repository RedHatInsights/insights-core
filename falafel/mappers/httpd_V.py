"""
httpd-V - Command httpd -V
==========================

Module for parsing the output of command ``httpd -V``. All contents are wrapped
into a dict.

Typical output of command ``httpd -V`` looks like:

    Server version: Apache/2.4.6 (Red Hat Enterprise Linux)
    Server's Module Magic Number: 20120211:24
    Compiled using: APR 1.4.8, APR-UTIL 1.5.2
    Architecture:   64-bit
    Server MPM:     prefork
    Server compiled with....
    -D APR_HAS_SENDFILE
    -D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
    -D AP_TYPES_CONFIG_FILE="conf/mime.types"
    -D SERVER_CONFIG_FILE="conf/httpd.conf"

Examples:
    >>> hv = shared[HttpdV]
    >>> hv['Server MPM']
    worker
    >>> hv["Server's Module Magic Number"]
    20120211:24
    >>> hv['Server compiled with']['APR_HAS_SENDFILE']
    True
    >>> hv['Server compiled with']['APR_HAVE_IPV6']
    'IPv4-mapped addresses enabled'
    >>> hv['Server compiled with']['SERVER_CONFIG_FILE']
    'conf/httpd.conf'

"""

from .. import Mapper, mapper, LegacyItemAccess


@mapper('httpd-V')
class HttpdV(LegacyItemAccess, Mapper):
    """Class for parsing ``httpd -V`` command output."""

    def parse_content(self, content):
        self.data = {}
        compiled_with = {}
        for line in content:
            line = line.strip()
            if ': ' in line:
                key, value = line.split(': ', 1)
                self.data[key.strip()] = value.strip()
            elif line.startswith('-'):
                line = line[3:]  # cut off the '-D '
                if '=' in line:
                    key, value = line.split('=', 1)
                    compiled_with[key] = value.strip('"')
                else:
                    key, _, value = line.partition(' ')
                    compiled_with[key] = value.strip('"()') if value else True

        self.data['Server compiled with'] = compiled_with

        return self.data
