"""
User and Group
==============

Module for processing the ``user`` and ``group`` of Linux.

Parsers provided by this module include:

GroupInfo - command ``getent group <groupname>``
------------------------------------------------

"""
from insights import parser, CommandParser
from insights.parsers import ParseException, SkipException, keyword_search
from insights.specs import Specs


@parser(Specs.group_info)
class GroupInfo(CommandParser, list):
    """
    Class to parse the output of ``getent group <groupname>``. The list of
    `groupname` is getting from the spec filters specified in rules.

    Typical output of the ``getent group <groupname>`` command is::

        wheel:x:10:admin,tester
        mem:x:8:

    Examples:

    >>> type(grp)
    <class 'insights.parsers.user_group.GroupInfo'>
    >>> grp[0]['id']
    10
    >>> grp[0]['name']
    'wheel'
    >>> grp[0]['users']
    ['admin', 'tester']
    """
    def parse_content(self, content):
        if not content:
            raise SkipException

        for line in content:
            try:
                row = line.split(':')
                self.append(
                    dict(
                        name=row[0],
                        id=int(row[2]),
                        users=row[-1].split(',') if row[-1] else []
                    )
                )
            except Exception as ex:
                raise ParseException(ex)

    def search(self, **kwargs):
        """
        Get the sub-list containing the keywords by searching the output of
        ``getent group <groupname>``

        This uses the :py:func:`insights.parsers.keyword_search` function for searching,
        see its documentation for usage details. If no search parameters are given or does
        match the search, then nothing will be returned.

        Returns:
            list: A list of dictionaries of the ``getent group <groupname>``
                  content that match the given search criteria.

        Examples:

        >>> grp.search(name='mem')[0] == grp[1]
        True
        >>> grp.search(users__contains='admin')[0] == grp[0]
        True
        """
        return keyword_search(self, **kwargs)
