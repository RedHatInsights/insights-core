"""
grubby - command ``/usr/sbin/grubby``
=====================================

This parser returns the output of the ``grubby --default-index`` command.

Examples:

    >>> default_index
    0
"""

from .. import parser
from insights.specs import Specs


@parser(Specs.grubby_default_index)
def grub2_default_index(context):
    """
    The output is the numeric index of the current default boot entry.
    Should be a int type value, count from 0.
    So we can return the content directly.
    """
    if context.content and context.content[0].isdigit():
        return int(context.content[0])
