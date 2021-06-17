"""
AnsibleTowerConfigCustom - file ``/etc/tower/conf.d/custom.py``
===============================================================
The AnsibleTowerConfigCustom class parses the file ``/etc/tower/conf.d/custom.py``.
"""
from insights import parser, get_active_lines, Parser
from insights.core.filters import add_filter
from insights.specs import Specs
from insights.parsers import SkipException

add_filter(Specs.ansible_tower_config_custom, ["AWX_CLEANUP_PATHS"])


@parser(Specs.ansible_tower_config_custom)
class AnsibleTowerConfigCustom(Parser, dict):
    """
    Class for content of ansible tower config file /etc/tower/conf.d/custom.py.

    Sample ``/etc/tower/conf.d/custom.py`` file::

        AWX_CLEANUP_PATHS = False

    Attributes:
        data (dict): A dict of "key=value" from configuration file

    Raises:
        SkipException: the file is empty or there is no valid content

    Examples::
    >>> type(conf)
    <class 'insights.parsers.ansible_tower_config_custom.AnsibleTowerConfigCustom'>
    >>> conf['AWX_CLEANUP_PATHS']
    'False'
    """

    def parse_content(self, content):
        """Parse content of of ansible tower config file '/etc/tower/conf.d/custom.py'"""
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
