"""
IrisList - Command ``/usr/bin/iris list``
=========================================

This parser reads the output of ``/usr/bin/iris list``.
"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.iris_list)
class IrisList(CommandParser, dict):
    """
    Parse the output of the ``/usr/bin/iris list`` command.

    Sample Input::

        Configuration 'IRIS'   (default)
            directory:    /intersystems
            versionid:    2023.1.0.235.1com
            datadir:      /intersystems
            conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
            status:       running, since Tue Jun 27 01:55:25 2023
            state:        ok
            product:      InterSystems IRIS

    Examples:
        >>> iris_info['name']
        'IRIS'
        >>> iris_info['status']
        'running, since Tue Jun 27 01:55:25 2023'
        >>> iris_info.is_running
        True
    """

    def parse_content(self, content):
        for line in content:
            if not line.strip():
                continue
            if line.strip().startswith('Configuration'):
                self['name'] = line.split()[1].strip('\'"')
            elif ":" in line:
                key, value = line.split(":", 1)
                self[key.strip()] = value.strip()

        if len(self) == 0:
            raise SkipComponent("The result is empty")

    @property
    def is_running(self):
        """Return True when the iris instance is running, and False when it is down"""
        return self.get('status', "").startswith('running')
