"""
getconf PAGE_SIZE - command ``/usr/sbin/getconf PAGE_SIZE``
=============================================

This very simple parser returns the output of the ``getconf PAGE_SIZE`` command.

    >>> output = shared[getconfpagesize]
    >>> output['value']
    '4096'
"""
from .. import parser
from insights.specs import Specs


@parser(Specs.getconf_page_size)
def getconfpagesize(context):
    """
    The output of "getconf PAGE_SIZE" command is in one of "4096", "8192",
    or "16384", so we can return the content directly.
    """
    return {"value": context.content[0]}
