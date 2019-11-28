"""
KSMState - file ``/sys/kernel/mm/ksm/run``
==========================================

Parser to get the kernel samepage merging state by reading the file
``/sys/kernel/mm/ksm/run``.
"""

from insights import parser, Parser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.ksmstate)
def is_running(context):
    """
    .. warning::
        This function parser is deprecated, please use :py:class:`KSMState`
        instead.

    Check if Kernel Samepage Merging is enabled. 'True' if KSM is
    on (i.e. ``/sys/kernel/mm/ksm/run`` is '1') or 'False' if not.
    """
    deprecated(is_running, "Use the `KSMState` class instead.")
    ksminfo = {}
    ksminfo['running'] = (context.content[0].split()[0] == '1')
    return ksminfo


@parser(Specs.ksmstate)
class KSMState(Parser):
    """
    Parser to get the kernel samepage merging state by reading the file
    ``/sys/kernel/mm/ksm/run``.

    Typical output of ``/sys/kernel/mm/ksm/run`` likes:

        0

    From https://www.kernel.org/doc/Documentation/vm/ksm.txt::

        set 0 to stop ksmd from running but keep merged pages,
        set 1 to run ksmd e.g. "echo 1 > /sys/kernel/mm/ksm/run",
        set 2 to stop ksmd and unmerge all pages currently merged, but leave
              mergeable areas registered for next run

    Examples:
        >>> ksm.value == '0'
        True
        >>> ksm.is_running
        False

    Raises:
        SkipException: when input is empty.
        ParseException: when the content is not expected.
    """
    def parse_content(self, content):
        if not content:
            raise SkipException
        if len(content) != 1 or content[0] not in ('0', '1', '2'):
            raise ParseException("Incorrect content: '{0}'".format(content))

        self.value = content[0]
        self.is_running = self.value == '1'
