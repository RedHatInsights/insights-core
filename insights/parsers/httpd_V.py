"""
HttpdV - command ``httpd -V``
=============================

Module for parsing the output of command ``httpd -V``.   The bulk of the
content is split on the colon and keys are kept as is.  Lines beginning with
'-D' are kept in a dictionary keyed under 'Server compiled with'; each
compilation option is a key in this sub-dictionary.  The value of the
compilation options is the value after the equals sign, if one is present,
or the value in brackets after the compilation option, or 'True' if only the
compilation option is present.
"""

from .. import Parser, parser, LegacyItemAccess
from insights.specs import Specs
from insights import SkipComponent


@parser(Specs.httpd_V)
class HttpdV(LegacyItemAccess, Parser):
    """
    Class for parsing ``httpd -V`` command output.

    The data is kept in the ``data`` property and can be accessed through the
    object itself thanks to the ``LegacyItemAccess`` parser class.

    Typical output of command ``httpd -V`` looks like::

        Server version: Apache/2.2.6 (Red Hat Enterprise Linux)
        Server's Module Magic Number: 20120211:24
        Compiled using: APR 1.4.8, APR-UTIL 1.5.2
        Architecture:   64-bit
        Server MPM:     Prefork
        Server compiled with....
        -D APR_HAS_SENDFILE
        -D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
        -D AP_TYPES_CONFIG_FILE="conf/mime.types"
        -D SERVER_CONFIG_FILE="conf/httpd.conf"

    Examples:
        >>> type(hv)
        <class 'insights.parsers.httpd_V.HttpdV'>
        >>> hv['Server MPM']
        'prefork'
        >>> hv["Server's Module Magic Number"]
        '20120211:24'
        >>> hv['Server compiled with']['APR_HAS_SENDFILE']
        True
        >>> hv['Server compiled with']['APR_HAVE_IPV6']
        'IPv4-mapped addresses enabled'
        >>> hv['Server compiled with']['SERVER_CONFIG_FILE']
        'conf/httpd.conf'

    Attributes:
        data (dict): The bulk of the content is split on the colon and keys are
            kept as is.  Lines beginning with '-D' are kept in a dictionary
            keyed under 'Server compiled with'; each compilation option is a key
            in this sub-dictionary.  The value of the compilation options is the
            value after the equals sign, if one is present, or the value in
            brackets after the compilation option, or 'True' if only the
            compilation option is present.
    """

    def parse_content(self, content):
        self.data = {}
        compiled_with = {}
        for line in content:
            line = line.strip()
            if ': ' in line:
                key, value = [s.strip() for s in line.split(': ', 1)]
                self.data[key] = value.lower()
            elif line.startswith('-'):
                line = line[3:]  # cut off the '-D '
                if '=' in line:
                    key, value = line.split('=', 1)
                    compiled_with[key] = value.strip('"')
                else:
                    if ' ' in line:
                        key, value = line.split(' ', 1)
                        value = value.strip('"()')
                    else:
                        key, value = line, True
                    compiled_with[key] = value

        self.data['Server compiled with'] = compiled_with


@parser(Specs.httpd_V)
class HttpdEventV(HttpdV):
    """
    Class for parsing ``httpd.event -V`` command output.

    Raises:
        SkipComponent: When no ``httpd.event -V`` command is found.
    """
    def parse_content(self, content):
        if 'event' in self.file_name:
            super(HttpdEventV, self).parse_content(content)
        else:
            raise SkipComponent("No 'httpd.event' command on this host.")


@parser(Specs.httpd_V)
class HttpdWorkerV(HttpdV):
    """
    Class for parsing ``httpd.worker -V`` command output.

    Raises:
        SkipComponent: When no ``httpd.worker -V`` command is found.
    """
    def parse_content(self, content):
        if 'worker' in self.file_name:
            super(HttpdWorkerV, self).parse_content(content)
        else:
            raise SkipComponent("No 'httpd.worker' command on this host.")
