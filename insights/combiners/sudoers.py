"""
Sudoers - files ``/etc/sudoers`` or ``/etc/sudoers.d/*``
========================================================

Module for combining the parsing results of ``/etc/sudoers`` and
``/etc/sudoers.d/*`` files.
"""
from insights import combiner
from insights.parsers.sudoers import SudoersBase, EtcSudoers


@combiner(EtcSudoers)
class Sudoers(SudoersBase):
    """
    Class to combiner the ``/etc/sudoers`` and ``/etc/sudoers.d/*``

    Attributes:
        lines(list): The list of RAW lines of all the ``/etc/sudoers`` and
            ``/etc/sudoers.d/*`` files. The order of lines keeps their original
            order them in files. And the files are read with `"filename`"
            alphabetical order.

    .. note::
        1. If there is not `"#includedir /etc/sudoers.d"` line in the entry
           file ``/etc/sudoers``, the ``/etc/sudoers.d/*`` files will be
           skipped.

        2. Two helper functions :func:`insights.parsers.sudoers.SudoersBase.get()`
           and :func:`insights.parsers.sudoers.SudoersBase.last()` are also
           provided to quickly get the specified line(s).
           For details, see the super-class:
           :class:`insights.parsers.sudoers.SudoersBase`.

    Examples:
        >>> type(sudo)
        <class 'insights.combiners.sudoers.Sudoers'>
        >>> sudo.get(['wheel', 'ALL=(ALL)', 'ALL'])
        ['%wheel  ALL=(ALL)       ALL']
        >>> sudo.last("#includedir")
        '#includedir /etc/sudoers.d'
    """
    def __init__(self, sudoers):
        self.lines = []
        first = False
        for sdr in sorted(sudoers, key=lambda x: x.file_path):
            self.lines.extend(sdr.lines)
            if not first:
                first = True
                include = sdr.last('#includedir')
                if not include or '/etc/sudoers.d' not in include.split()[-1]:
                    break
