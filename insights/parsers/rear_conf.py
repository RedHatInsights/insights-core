"""
RearLocalConf - File /etc/rear/local.conf
=========================================
"""

from insights.core import TextFileOutput
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.rear_local_conf)
class RearLocalConf(TextFileOutput):
    """
    Parses content of "/etc/rear/local.conf".

    Typical content of "/etc/rear/local.conf" is::

        BACKUP_RESTORE_MOVE_AWAY_FILES=( /boot/grub/grubenv /boot/grub2/grubenv )


    Examples:
        >>> type(local_conf)
        <class 'insights.parsers.rear_conf.RearLocalConf'>
        >>> local_conf.lines[0] == 'BACKUP_RESTORE_MOVE_AWAY_FILES=( /boot/grub/grubenv /boot/grub2/grubenv )'
        True
    """

    def parse_content(self, content):
        content = get_active_lines(content)
        if not content:
            raise SkipComponent
        super(RearLocalConf, self).parse_content(content)
