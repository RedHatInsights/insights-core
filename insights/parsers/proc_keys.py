"""
ProcKeys - File ``/proc/keys``
==============================

This parser reads the content of ``/proc/keys``.

"""

from insights import Parser, parser
from insights.parsers import SkipException, keyword_search
from insights.specs import Specs


@parser(Specs.proc_keys)
class ProcKeys(Parser, list):
    """
    Class ``ProcKeys`` parses the content of the ``/proc/keys`` file.

    This file exposes a list of the keys for which the reading thread has view
    permission, providing various information about each key. The fields shown
    in each line of this file contains below attributes::

        ID (string):            The ID of the key, expressed in hexadecimal.
        Flags (string):         A set of flags describing the state of the key
        Usage (string):         The count of the number of kernel credential structures
                                that are pinning the key.
        Timeout (string):       The amount of time until the key will expire (weeks, days,
                                hours, minutes, and seconds). The string perm here means
                                that the key is permanent (no timeout). The string expd
                                means that the key has already expired, but has not yet
                                been garbage collected.
        Permissions (string):   The key permissions, expressed as four hexadecimal bytes
                                containing, from left to right, the possessor, user, group,
                                and other permissions.
        UID (string):           The user ID of the key owner.
        GID (string):           The group ID of the key.
        Type (string) :         The key type.
        Description (string)    The key description (name). For most key types, it has the
                                form name[: extra-info]. (The name subfield is the key's
                                description (name). The optional extra-info field provides
                                some further information about the key.)


    Sample output::

        009a2028 I--Q---   1 perm 3f010000  1000  1000 user     krb_ccache:primary: 12
        1806c4ba I--Q---   1 perm 3f010000  1000  1000 keyring  _pid: 2
        25d3a08f I--Q---   1 perm 1f3f0000  1000 65534 keyring  _uid_ses.1000: 1
        28576bd8 I--Q---   3 perm 3f010000  1000  1000 keyring  _krb: 1
        2c546d21 I--Q--- 190 perm 3f030000  1000  1000 keyring  _ses: 2
        30a4e0be I------   4   2d 1f030000  1000 65534 keyring  _persistent.1000: 1
        32100fab I--Q---   4 perm 1f3f0000  1000 65534 keyring  _uid.1000: 2
        32a387ea I--Q---   1 perm 3f010000  1000  1000 keyring  _pid: 2
        3ce56aea I--Q---   5 perm 3f030000  1000  1000 keyring  _ses: 1


    Examples:
        >>> type(proc_keys)
        <class 'insights.parsers.proc_keys.ProcKeys'>
        >>> proc_keys[0]['id']
        '009a2028'
        >>> proc_keys[0]['flags']
        'I--Q---'
        >>> proc_keys[0]['usage']
        '1'
        >>> proc_keys[0]['timeout']
        'perm'
        >>> proc_keys[0]['permissions']
        '3f010000'
        >>> proc_keys[0]['uid']
        '1000'
        >>> proc_keys[0]['gid']
        '1000'
        >>> proc_keys[0]['type']
        'user'
        >>> proc_keys[0]['description']
        'krb_ccache:primary: 12'
    """

    def parse_content(self, content):

        if not content:
            raise SkipException("No Contents")

        column = ['id', 'flags', 'usage', 'timeout', 'permissions', 'uid', 'gid', 'type', 'description']

        for line in content:
            row = line.split(None, 8)
            if row and len(column) == len(row):
                self.append(dict(zip(column, row)))
            else:
                raise SkipException("Invalid Contents: {0}".format(line))

    def search(self, **kwargs):
        """
        Get the sublist containing the keywords by searching the ``/proc/keys`` list.

        This uses the :py:func:`insights.parsers.keyword_search` function for searching,
        see its documentation for usage details. If no search parameters are given or does
        match the search, then nothing will be returned.

        Returns:
            list: A list of dictionaries of the ``/proc/keys`` content that match the given search criteria.

        Examples:
            >>> proc_keys.search(timeout='perm')[0] == proc_keys[0]
            True
            >>> proc_keys.search(description__contains='uid')[0] == proc_keys[2]
            True
        """
        return keyword_search(self, **kwargs)
