"""
Parsers for watchdog configuration
==================================

WatchDogConf - file ``/etc/watchdog.conf``
------------------------------------------
"""

from insights import parser, Parser, SkipComponent
from insights.specs import Specs
from insights.parsers import split_kv_pairs


@parser(Specs.watchdog_conf)
class WatchDogConf(Parser, dict):
    """
    Parsing the `/etc/watchdog.conf` file. It stores the data in a dict.

    Sample content::

        # The retry-timeout and repair limit are used to handle errors in a
        # more robust manner. Errors must persist for longer than this to
        # action a repair or reboot, and if repair-maximum attempts are
        # made without the test passing a reboot is initiated anyway.

        retry-timeout          = 60
        repair-maximum         = 1
        realtime               = yes
        priority               = 1

    Examples:
        >>> 'retry-timeout' in watchdog_conf_obj
        True
        >>> 'test-timeout' in watchdog_conf_obj
        False
        >>> watchdog_conf_obj.get('retry-timeout')
        '60'
        >>> watchdog_conf_obj.get('realtime')
        'yes'
    """
    def parse_content(self, content):
        self.update(split_kv_pairs(content))
        if not self:
            raise SkipComponent('Not available data')
