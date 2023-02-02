"""
KTimerLockless - file ``/sys/kernel/ktimer_lockless_check``
===========================================================
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ktimer_lockless)
class KTimerLockless(Parser):
    """
    The KTimerLockless class parses the file ``/sys/kernel/ktimer_lockless_check``.

    Typical output of ``/sys/kernel/ktimer_lockless_check`` file:

        0

    Examples:
        >>> ktimer_lockless.ktimer_lockless_val
        0

    Raises:
        SkipComponent: when input is empty.
    """
    def parse_content(self, content):
        if len(content) == 1 and content[0].isdigit():
            self.ktimer_lockless_val = int(content[0])
        else:
            raise SkipComponent('The file is empty')
