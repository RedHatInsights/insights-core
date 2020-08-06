"""
``/sys/module`` System Module Information
=========================================

A parser to parse the system module information.

Parsers included in this module are:

DMModUseBlkMq - file ``/sys/module/dm_mod/parameters/use_blk_mq``

SCSIModUseBlkMq - file ``/sys/module/scsi_mod/parameters/use_blk_mq``
------------------------------------------------------------

"""


from insights import parser, Parser
from insights.parsers import SkipException
from insights.specs import Specs


class XModUseBlkMq(Parser):
    """
    Parse for file `/sys/module/{dm_mod,scsi_mod}/parameters/use_blk_mq`.
    File content shows if use_blk_mq parameter is on.

    Sample Content::

        Y - for on
        N - for off
    """

    def parse_content(self, content):
        if not content or len(content) != 1:
            raise SkipException()
        self.val = content[0].strip()

    @property
    def is_on(self):
        """
        Returns (bool or None): True for on, False for off, None for unknow case.
        """
        return True if self.val == 'Y' else (False if self.val == 'N' else None)


@parser(Specs.dm_mod_use_blk_mq)
class DMModUseBlkMq(XModUseBlkMq):
    """
    This file `/sys/module/dm_mod/parameters/use_blk_mq` shows if use_blk_mq
    parameter is on.

    Examples::

        >>> dm_mod_use_blk_mq.val
        'Y'
        >>> dm_mod_use_blk_mq.is_on
        True

    Raises:
        SkipException: When contents are empty
    """
    pass


@parser(Specs.scsi_mod_use_blk_mq)
class SCSIModUseBlkMq(XModUseBlkMq):
    """
    This file `/sys/module/scsi_mod/parameters/use_blk_mq` shows if use_blk_mq
    parameter is on.

    Examples::

        >>> scsi_mod_use_blk_mq.val
        'N'
        >>> scsi_mod_use_blk_mq.is_on
        False

    Raises:
        SkipException: When contents are empty
    """
    pass
