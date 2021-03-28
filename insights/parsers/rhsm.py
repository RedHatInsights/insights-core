"""
Red Hat Subscription-Manager - Commands
==============
Parsers for ``subscription-manager`` commands.

This module contains the classes that parse the output of the commands
`subscription-manager repos --list-enabled`.

RHSMEnabledRepoList - command ``subscription-manager repos --list-enabled``
-----------------------------------------
"""

from insights import parser, CommandParser
from insights.parsers import SkipException, parse_fixed_table
from insights.specs import Specs

eus = [
    '5.0.z',
    '5.1.z',
    '5.2.z',
    '5.3.ll',
    '5.3.z',
    '5.4.z',
    '5.6.ll',
    '5.6.z',
    '5.9.ll',
    '5.9.z'
    '6.0.z',
    '6.1.z',
    '6.2.aus',
    '6.2.z',
    '6.3.z',
    '6.4.aus',
    '6.4.z',
    '6.5.aus',
    '6.5.z',
    '6.6.aus',
    '6.6.z',
    '6.7.z'
]


@parser(Specs.rhsm_enabledrepolist)
class RHSMEnabledRepoList(CommandParser):
    """
    Class for parsing the output of `subscription-manager repos --list-enabled` command.

    Typical output of the command is::

    Repo ID:   rhel-8-for-x86_64-baseos-rpms
    Repo Name: Red Hat Enterprise Linux 8 for x86_64 - BaseOS (RPMs)
    Repo URL:  <URL>

    Examples:
        >>> len(repolist)
        3
        >>> 'rhel-7-server-e4s-rpms/x86_64' in repolist.repos
        True
        >>> 'rhel-7-server-e4s-rpms' in repolist.repos
        False
        >>> 'rhel-7-server-e4s-rpms' in repolist.rhel_repos
        True
        >>> repolist['rhel-7-server-e4s-rpms/x86_64']['name']
        'Red Hat Enterprise Linux 7 Server - Update Services for SAP Solutions (RPMs)'
        >>> repolist[0]['name']
        'Red Hat Enterprise Linux 7 Server - Update Services for SAP Solutions (RPMs)'
        >>> repolist['rhel-ha-for-rhel-7-server-e4s-rpms/x86_64']['id']
        '!rhel-ha-for-rhel-7-server-e4s-rpms/x86_64'
        >>> len(repolist_no_reponame)
        13
        >>> len(repolist_no_reponame.rhel_repos)
        3
        >>> 'rhel-6-server-rpms' in repolist_no_reponame.repos
        True
        >>> 'rhel-6-server-optional-rpms' in repolist_no_reponame.rhel_repos
        True
        >>> repolist_no_reponame[0]['id']
        'LME_EPEL_6_x86_64'
        >>> repolist_no_reponame[0].get('name', '')
        ''

    Attributes:
        data (list): list of repos wrapped in dictionaries
        repos (dict): dict of all listed repos where the key is the full repo-id without "!" or "*".
            But you can get it from the value part if needed. For example::

                self.repos = {
                    'rhel-7-server-e4s-rpms/x86_64': {
                        'id': 'rhel-7-server-e4s-rpms/x86_64',
                        'name': 'Red Hat Enterprise Linux 7 Server - Update Services for SAP Solutions (RPMs)',
                        'status': '12,250'
                    },
                    'rhel-ha-for-rhel-7-server-e4s-rpms/x86_64': {
                        'id': '!rhel-ha-for-rhel-7-server-e4s-rpms/x86_64',
                        'name': 'Red Hat Enterprise Linux High Availability (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)',
                        'status': '272'
                    },
                    'rhel-sap-hana-for-rhel-7-server-e4s-rpms/x86_64': {
                        'id': '*rhel-sap-hana-for-rhel-7-server-e4s-rpms/x86_64',
                        'name': 'RHEL for SAP HANA (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)',
                        'status': '21'
                    }
                }

        rhel_repos(list): list of all the rhel repos and the item is just the repo id without server and arch info. For example::

            self.rhel_repos = ['rhel-7-server-e4s-rpms', 'rhel-ha-for-rhel-7-server-e4s-rpms', 'rhel-sap-hana-for-rhel-7-server-e4s-rpms']
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('No repolist.')

        self.data = []
        self.repos = {}

        repoid = ""
        for line in content.splitlines():
            if('Repo ID:' in line):
                repoid = line.split('Repo ID:')[1].strip()
            if('Repo Name:' in line):
                reponame = line.split('Repo Name:')[1].strip()
                self.data.append({'id': repoid, 'name': reponame})

        if not self.data:
            raise SkipException('No repolist.')

        self.repos = dict((d['id'].lstrip('!').lstrip('*'), d) for d in self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.data[idx]
        elif isinstance(idx, str):
            return self.repos[idx]

    def __contains__(self, _id):
        return _id in self.repos

    @property
    def eus(self):
        '''list of the EUS part of each repo'''
        euses = []
        for repo in [r["id"] for r in self.data]:
            if repo.startswith("rhel-") and "server-" in repo:
                _, eus_version = repo.split("server-", 1)
                if eus_version in eus:
                    euses.append(eus_version)
        return euses

    @property
    def rhel_repos(self):
        '''list of RHEL repos/Repo IDs'''
        return [i.split('/')[0]
                for i in self.repos
                if i.startswith('rhel')]
