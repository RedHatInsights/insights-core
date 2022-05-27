"""
Sudoers - files ``/etc/sudoers`` or ``/etc/sudoers.d/*``
========================================================

Module for combining the parsing results of ``/etc/sudoers`` and
``/etc/sudoers.d/*`` files.

"""
from insights import combiner
from insights.parsers.sudoers import EtcSudoers


@combiner(EtcSudoers)
class Sudoers(object):
    """
    Class to combiner the ``/etc/sudoers`` and ``/etc/sudoers.d/*``

    Attributes:
        lines(list): The list of RAW lines of all the ``/etc/sudoers`` and
            ``/etc/sudoers.d/*``files. The order of lines keeps their original
            order them in files. And the files are read with "filename"
            alphabetical order.

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
        for sdr in sorted(sudoers, key=lambda x: x.file_path):
            self.lines.extend(sdr.lines)

    def get(self, s, check=all):
        """
        Returns all lines that contain `s` anywhere and return the list of RAW
        line directly. `s` can be either a single string or a string list. For
        list, all keywords in the list must be found in each line.

        Parameters:
            s(str or list): one or more strings to search for
            check(func): built-in function ``all`` or ``any`` applied to each line

        Returns:
            (list): list of lines that contain the `s`.

        Raises:
            TypeError: When `s` is not a string or a list of strings, or `num`
                is not an integer.
        """
        def _valid_search(s, check=all):
            if isinstance(s, str):
                return lambda l: s in l
            elif (isinstance(s, (tuple, list)) and len(s) > 0 and
                  all(isinstance(w, str) for w in s)):
                return lambda l: check(w in l for w in s)
            raise TypeError('"s" must be given as a string or a list of strings')

        search_by_expression = _valid_search(s, check)
        ret = []
        for _l in self.lines:
            if search_by_expression(_l):
                ret.append(_l)
        return ret

    def last(self, s, check=all):
        """
        Returns the last line that contain `s` anywhere and return the RAW
        line directly. `s` can be either a single string or a string list. For
        list, all keywords in the list must be found in each line.

        Parameters:
            s(str or list): one or more strings to search for
            check(func): built-in function ``all`` or ``any`` applied to each line

        Returns:
            (str): The line that contains the `s`. None by default.

        Raises:
            TypeError: When `s` is not a string or a list of strings, or `num`
                is not an integer.
        """
        ret = self.get(s, check)
        return ret[-1] if ret else None
