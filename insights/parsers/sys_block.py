"""
System block files under ``/sys/block``
=======================================

This module contains the following parsers:

StableWrites - file ``/sys/block/*/queue/stable_writes``
--------------------------------------------------------
"""
from insights import Parser, parser
from insights.core.exceptions import ParseException
from insights.specs import Specs


@parser(Specs.sys_block_queue_stable_writes)
class StableWrites(Parser):
    """
    Class for parsing the ``/sys/block/*/queue/stable_writes`` files.

    Typical content of the file is::

        1

    Examples:
        >>> type(block_stable_writes)
        <class 'insights.parsers.sys_block.StableWrites'>
        >>> block_stable_writes.stable_writes
        1
        >>> block_stable_writes.device
        'sda'

    Raises:
        ParseException: When content is empty or unparsable
    """

    def parse_content(self, content):
        if len(content) != 1:
            raise ParseException('Error: {0}'.format(content if content else 'empty file'))
        try:
            self._stable_writes = int(content[0].strip())
            self._device = self.file_path.split('/')[-3]
        except ValueError:
            raise ParseException("Error: unparsable content: {0}".format(content[0]))

    @property
    def stable_writes(self):
        """ int: Value of ``stable_writes``."""
        return self._stable_writes

    @property
    def device(self):
        """ str: Block device name from file path."""
        return self._device
