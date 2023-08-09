"""
Sudoers - files ``/etc/sudoers`` and ``/etc/sudoers.d/*``
=========================================================

Module for processing each of the ``/etc/sudoers`` and ``/etc/sudoers.d/*`` files.

.. note::
    These files is filtered to skip the sensitive information.

.. note::
    Please use the :py:class:`insigths.combiners.suoders.Sudoers` for global
    checking.

"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs

add_filter(Specs.sudoers, "#includedir")
"""The "#includedir" is the line that should be always collected. """


class SudoersBase(object):
    """
    Base class for parsing the files ``/etc/sudoers`` or ``/etc/sudoers.d/*``,
    it provides the following two helper functions ``get`` and ``last``.
    """
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


@parser(Specs.sudoers)
class EtcSudoers(Parser, SudoersBase):
    """
    Class to parse the files ``/etc/sudoers`` or ``/etc/sudoers.d/*``

    Typical content of the  ``/etc/sudoers`` and ``/etc/sudoers.d/*`` is::

        ## Allows people in group wheel to run all commands
        %wheel  ALL=(ALL)       ALL
        ## Read drop-in files from /etc/sudoers.d (the # here does not mean a comment)
        #includedir /etc/sudoers.d

    Attributes:
        lines(list): The list of RAW lines of the file.

    .. note::
        The super-class :class:`SudoersBase` providers two helper functions:
        :func:`SudoersBase.get()` and :func:`SudoersBase.last()`.


    Examples:
        >>> type(sudo)
        <class 'insights.parsers.sudoers.EtcSudoers'>
        >>> len(sudo.lines)
        2
        >>> sudo.get(['wheel', 'ALL=(ALL)', 'ALL'])
        ['%wheel  ALL=(ALL)       ALL']
        >>> sudo.last("#includedir")
        '#includedir /etc/sudoers.d'
    """
    def parse_content(self, content):
        self.lines = get_active_lines(content, comment_char="##")

        if not self.lines:
            raise SkipComponent
