"""
KpatchList - command ``/usr/sbin/kpatch list``
=================================================

The ``/usr/sbin/kpatch list`` command provides information about
the installed patch modules.

Sample content from command ``/usr/sbin/kpatch list`` is::
    Loaded patch modules:
    kpatch_3_10_0_1062_1_1_1_4 [enabled]

    Installed patch modules:
    kpatch_3_10_0_1062_1_1_1_4 (3.10.0-1062.1.1.el7.x86_64)

Examples:
    >>> 'kpatch_3_10_0_1062_1_1_1_4' in kpatchs.loaded
    True
    >>> kpatchs.loaded.get('kpatch_3_10_0_1062_1_1_1_4')
    'enabled'
    >>> 'kpatch_3_10_0_1062_1_1_1_4' in kpatchs.installed
    True
    >>> kpatchs.installed.get('kpatch_3_10_0_1062_1_1_1_4')
    '3.10.0-1062.1.1.el7.x86_64'
"""

from insights.specs import Specs
from insights.parsers import SkipException
from insights import parser, CommandParser


@parser(Specs.kpatch_list)
class KpatchList(CommandParser):
    """Class for command: /usr/sbin/kpatch list"""
    def parse_content(self, content):
        if content is None or len(content) == 0:
            raise SkipException("No Data from command: /usr/sbin/kpatch list")

        self._loaded = {}
        self._installed = {}
        cur_dict = {}
        for line in content:
            if 'Loaded patch modules' in line:
                cur_dict = self._loaded
                continue

            if 'Installed patch modules' in line:
                cur_dict = self._installed
                continue

            if '[' in line or ']' in line:
                line = line.replace('[', '').replace(']', '')

            if '(' in line or ')' in line:
                line = line.replace('(', '').replace(')', '')

            fields = line.split(' ')
            if len(fields) != 2:
                # invalid line
                continue

            cur_dict[fields[0]] = fields[1]

    @property
    def loaded(self):
        """Returns the loaded kpatchs"""
        return self._loaded

    @property
    def installed(self):
        """Returns the installed kpatchs"""
        return self._installed
