"""
SELinux Policy Management tool
==============================

This module contains the following parsers:

SemanageLoginList - command ``semanage login -l``
-------------------------------------------------
"""

from insights.specs import Specs
from insights import Parser, parser
from insights.parsers import parse_fixed_table, keyword_search


@parser(Specs.semanage_login_list)
class SemanageLoginList(Parser, list):
    """
    Parse the output of the command ``semanage login -l``.
    It returns a list of dict like::

        [
            {
                'login_name': '__default__',
                'selinux_user': 'unconfined_u',
                'mls_mcs_range': 's0-s0:c0.c1023',
                'service': '*',
            },
            {
                'login_name': 'root',
                'selinux_user': 'unconfined_u',
                'mls_mcs_range': 's0-s0:c0.c1023',
                'service': '*',
            },

        ]

    Sample output::

        Login Name           SELinux User         MLS/MCS Range        Service

        __default__          unconfined_u         s0-s0:c0.c1023       *
        root                 unconfined_u         s0-s0:c0.c1023       *
        system_u             system_u             s0-s0:c0.c1023       *

    Examples:
        >>> unconfined_users = users.search(selinux_user='unconfined_u')
        >>> len(unconfined_users)
        2
        >>> unconfined_users[0]['login_name']
        '__default__'
    """
    def parse_content(self, content):
        data = parse_fixed_table(
            content,
            heading_ignore=['Login Name'],
            header_substitute=[
                ('Login Name', 'login_name'),
                ('SELinux User', 'selinux_user'),
                ('MLS/MCS Range', 'mls_mcs_range'),
                ('Service', 'service'),
            ]
        )
        self.extend(data)

    def search(self, **kwargs):
        """
        Return a list of selinux users by searching the rows with kwargs.

        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details. If no search
        parameters are given, no rows are returned.
        """
        return keyword_search(self, **kwargs)
