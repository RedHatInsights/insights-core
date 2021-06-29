"""
AnsibleTowerSettings - file ``/etc/tower/conf.d/*.py`` and ``/etc/tower/settings.py``
=====================================================================================
The AnsibleTowerSettings class parses the file ``/etc/tower/conf.d/*.py`` and
``/etc/tower/settings.py``.
"""
from insights import parser, get_active_lines, Parser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.ansible_tower_settings)
class AnsibleTowerSettings(Parser, dict):
    """
    Class for content of ansible tower config file ``/etc/tower/conf.d/*.py`` and ``/etc/tower/settings.py``.

    Sample ``/etc/tower/conf.d/*.py`` file::

        AWX_CLEANUP_PATHS = False

    Raises:
        SkipException: the file is empty or there is no valid content

    Examples::
    >>> type(conf)
    <class 'insights.parsers.ansible_tower_settings.AnsibleTowerSettings'>
    >>> conf['AWX_CLEANUP_PATHS']
    'False'
    """

    def parse_content(self, content):
        """Parse content of of ansible tower config file ``/etc/tower/conf.d/*.py`` and ``/etc/tower/settings.py``"""
        if not content:
            raise SkipException("No Valid Configuration")
        data = {}
        for line in get_active_lines(content):
            if "=" in line:
                key, value = line.split("=")
                data[key.strip()] = value.strip()
        if not data:
            raise SkipException("No Valid Configuration")
        self.update(data)
