"""
Modules load configuration - files ``/etc/modules-load.d/*.conf``
=================================================================

This parser reads the pre-load kernel module names from
``/etc/modules-load.d/*.conf`` files.
"""

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.modules_load_d)
class ModulesLoadD(Parser, dict):
    """
    Parse the ``/etc/modules-load.d/*.conf`` files.

    This parser reads the modules-load.d files and stores the filename and
    corresponding content as key–value pairs in a dictionary.

    Sample input from file ``/etc/modules-load.d/cifs.conf``::

        cifs

    Examples:
        >>> 'cifs.conf' in modules_load
        True
        >>> modules_load['cifs.conf']
        'cifs'
    """

    def parse_content(self, content):
        filename = self.file_path.rsplit('/', 1)[-1]
        self[filename] = content[0] if content else ''
