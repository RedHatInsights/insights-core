"""
KpatchList - command ``/usr/sbin/kpatch list``
==============================================

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
        if not content:
            raise SkipException("No Data from command: /usr/sbin/kpatch list")

        self._loaded = {}
        self._installed = {}
        cur_dict = {}
        for line in content:
            if not line.strip():
                continue

            if 'Loaded patch modules' in line:
                cur_dict = self._loaded
                continue

            if 'Installed patch modules' in line:
                cur_dict = self._installed
                continue

            fields = [k.strip('()[]') for k in line.split()]
            if len(fields) == 1:
                if cur_dict == self._loaded:
                    # In the early version:
                    #  # kpatch list
                    #  Loaded patch modules:
                    #  kpatch_7_0_1_el7
                    #
                    cur_dict[fields[0].strip()] = ''

            elif len(fields) == 2:
                cur_dict[fields[0]] = fields[1]

    @property
    def loaded(self):
        """
        (dict): This will return the loaded kpath modules
        """
        return self._loaded

    @property
    def installed(self):
        """
        (dict): This will return the installed kpath modules
        """
        return self._installed
