"""
HttpdM - command ``httpd -M``
=============================

Module for parsing the output of command ``httpd -M``.
"""
from insights.core import CommandParser, LegacyItemAccess
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.httpd_M)
class HttpdM(LegacyItemAccess, CommandParser):
    """
    Class for parsing ``httpd -M`` command output.

    The data is kept in the ``data`` property and can be accessed through the
    object itself thanks to the ``LegacyItemAccess`` parser class.

    Typical output of command ``httpd -M`` looks like::

        Loaded Modules:
         core_module (static)
         http_module (static)
         access_compat_module (shared)
         actions_module (shared)
         alias_module (shared)
        Syntax OK

    Examples:
        >>> type(hm)
        <class 'insights.parsers.httpd_M.HttpdM'>
        >>> len(hm.loaded_modules)
        5
        >>> len(hm.static_modules)
        2
        >>> 'core_module' in hm.static_modules
        True
        >>> 'http_module' in hm.static_modules
        True
        >>> 'http_module' in hm
        True
        >>> 'http_module' in hm.shared_modules
        False
        >>> hm.httpd_command
        '/usr/sbin/httpd'

    Raise:
        ParseException: When input content is empty or there is no parsed data.

    Attributes:
        data (dict): All loaded modules are stored in this dictionary with the
                     name as the key and the loaded mode ('shared' or 'static')
                     as the value.
        loaded_modules (list): List of the loaded modules.
        static_modules (list): List of the loaded static modules.
        shared_modules (list): List of the loaded shared modules.
    """

    def parse_content(self, content):
        if not content:
            raise ParseException("Input content is empty.")

        self.data = {}
        self.loaded_modules = []
        self.static_modules = []
        self.shared_modules = []
        IGNORE_LINES = ('Loaded Modules:', 'Syntax')
        for line in content:
            if line.startswith((IGNORE_LINES)):
                continue
            line_splits = line.strip().split()
            if len(line_splits) == 2:
                module, mode = line_splits[0], line_splits[-1].strip("()")
                self.data[module] = mode

        if self.data:
            self.loaded_modules = self.data.keys()
            self.static_modules = [k for k, v in self.data.items() if v == 'static']
            self.shared_modules = [k for k, v in self.data.items() if v == 'shared']
        else:
            raise ParseException("Input content is not empty but there is no useful parsed data.")

    @property
    def httpd_command(self):
        """
        Return the full binary path of a running httpd or None when nothing
        is found. It's to identify which httpd binaries the instance run with.
        """
        return self.args
