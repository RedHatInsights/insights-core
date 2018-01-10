"""
Kernel Samepage Merging state - file ``/sys/kernel/mm/ksm/run``
===============================================================

This module offers the ``is_running`` parser function, which returns a
dictionary with one key: 'running', whose value is the state of whether
Kernel Samepage Merging is turned on.

Examples:

    >>> ksm = shared[is_running]
    >>> ksm['running']
    False
"""

from .. import parser
from insights.specs import Specs


@parser(Specs.ksmstate)
def is_running(context):
    """
    Check if Kernel Samepage Merging is turned on. Returns 'True' if KSM is
    on (i.e. ``/sys/kernel/mm/ksm/run`` is '1') or 'False' if not.
    """
    ksminfo = {}
    ksminfo['running'] = (context.content[0].split()[0] == '1')
    return ksminfo
