"""
OsslFilesConfig - Commands ``/usr/lib/dracut/ossl-files --config``
==================================================================
Classes to parse ``/usr/lib/dracut/ossl-files --config`` command information.

"""

from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ossl_files)
class OsslFilesConfig(Parser):
    """
    Parses output of ``/usr/lib/dracut/ossl-files --config`` command.

    Attributes:
        error_lines (list): List of error lines.
        conf_path (str): Configuration file path of OpenSSL.

    Sample input::

        /etc/pki/tls/openssl.cnf

    Examples:
        >>> type(openssl_cnf)
        <class 'insights.parsers.ossl_files.OsslFilesConfig'>
        >>> openssl_cnf.conf_path
        '/etc/pki/tls/openssl.cnf'
    """

    def parse_content(self, content):
        self.conf_path = None
        self.error_lines = []

        if len(content) == 1:
            line = content[0].strip()
            if line and line.startswith('/'):
                self.conf_path = line
            else:
                self.error_lines.append(line)
        else:
            for line in content:
                self.error_lines.append(line.strip())

        if not self.conf_path and not self.error_lines:
            raise SkipComponent
