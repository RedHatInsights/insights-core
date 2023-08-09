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
from insights.core import CommandParser, LegacyItemAccess
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.httpd_V)
class HttpdV(LegacyItemAccess, CommandParser):
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
        >>> hv.mpm
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

    Raises:
        SkipComponent: When input content is empty or there is no parsed data.
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Input content is empty.")

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

        if self.data:
            if compiled_with:
                self.data['Server compiled with'] = compiled_with
        else:
            raise SkipComponent("Input content is not empty but there is no useful parsed data.")

    @property
    def httpd_command(self):
        """
        Return the full binary path of a running httpd or None when nothing
        is found. It's to identify which httpd binaries the instance run with.
        """
        return self.args

    @property
    def mpm(self):
        """
        str: The MPM mode of the running httpd. An Empty string when nothing
        is found.
        """
        return self.data.get('Server MPM', '')

    @property
    def version(self):
        """
        str: The version of the running httpd. An Empty string when nothing
        is found.
        """
        return self.get('Server version', '')
