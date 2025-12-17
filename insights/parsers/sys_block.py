"""
System block files under ``/sys/block``
=======================================

This module contains the following parsers:

StableWrites - file ``/sys/block/*/queue/stable_writes``
--------------------------------------------------------
DiscardMaxBytes - file ``/sys/block/*/queue/discard_max_bytes``
---------------------------------------------------------------
MaxSegmentSize - file ``/sys/block/*/queue/max_segment_size``
--------------------------------------------------------------
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


@parser(Specs.sys_block_queue_discard_max_bytes)
class DiscardMaxBytes(Parser):
    """
    Class for parsing the ``/sys/block/*/queue/discard_max_bytes`` files.

    Typical content of the file is::

        2147483648

    Examples:
        >>> type(block_discard_max_bytes)
        <class 'insights.parsers.sys_block.DiscardMaxBytes'>
        >>> block_discard_max_bytes.discard_max_bytes
        2147483648
        >>> block_discard_max_bytes.device
        'sda'

    Raises:
        ParseException: When content is empty or unparsable
    """

    def parse_content(self, content):
        if len(content) != 1:
            raise ParseException('Error: {0}'.format(content if content else 'empty file'))
        try:
            self._discard_max_bytes = int(content[0].strip())
            self._device = self.file_path.split('/')[-3]
        except ValueError:
            raise ParseException("Error: unparsable content: {0}".format(content[0]))

    @property
    def discard_max_bytes(self):
        """ int: Value of ``discard_max_bytes``."""
        return self._discard_max_bytes

    @property
    def device(self):
        """ str: Block device name from file path."""
        return self._device


@parser(Specs.sys_block_queue_max_segment_size)
class MaxSegmentSize(Parser):
    """
    Class for parsing the ``/sys/block/*/queue/max_segment_size`` files.

    Typical content of the file is::

        65536

    Examples:
        >>> type(block_max_segment_size)
        <class 'insights.parsers.sys_block.MaxSegmentSize'>
        >>> block_max_segment_size.max_segment_size
        65536
        >>> block_max_segment_size.device
        'sda'

    Raises:
        ParseException: When content is empty or unparsable
    """

    def parse_content(self, content):
        if len(content) != 1:
            raise ParseException('Error: {0}'.format(content if content else 'empty file'))
        try:
            self._max_segment_size = int(content[0].strip())
            self._device = self.file_path.split('/')[-3]
        except ValueError:
            raise ParseException("Error: unparsable content: {0}".format(content[0]))

    @property
    def max_segment_size(self):
        """ int: Value of ``max_segment_size``."""
        return self._max_segment_size

    @property
    def device(self):
        """ str: Block device name from file path."""
        return self._device
