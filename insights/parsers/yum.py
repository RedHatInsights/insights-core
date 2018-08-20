"""
Yum - Commands
==============
Parsers for ``yum`` commands.

This module contains the classes that parse the output of the commands
`yum -C repolist`.

YumRepoList - command ``yum -C repolist``
-----------------------------------------
"""
from insights import parser, CommandParser
from insights.parsers import SkipException
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


@parser(Specs.yum_repolist)
class YumRepoList(CommandParser):
    """
    Class for parsing the output of `yum -C repolist` command.

    Typical output of the command is::

        Loaded plugins: langpacks, product-id, search-disabled-repos, subscription-manager
        repo id                                             repo name                                                                                                    status
        rhel-7-server-e4s-rpms/x86_64                       Red Hat Enterprise Linux 7 Server - Update Services for SAP Solutions (RPMs)                                 12,250
        rhel-ha-for-rhel-7-server-e4s-rpms/x86_64           Red Hat Enterprise Linux High Availability (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)         272
        rhel-ha-for-rhel-7-server-rpms/x86_64               Red Hat Enterprise Linux High Availability (for RHEL 7 Server) (RPMs)                                           225
        rhel-sap-hana-for-rhel-7-server-e4s-rpms/x86_64     RHEL for SAP HANA (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)                                   21
        repolist: 12,768

    Examples:
        >>> len(repolist)
        4
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

    Attributes:
        data (list): list of repos wrapped in dictionaries
        repos (dict): dict of all listed repos where the key is the full repo-id

    """
    def parse_content(self, content):
        self.data = []
        self.repos = {}
        found_start = False
        for line in content:
            if line.startswith("repolist:"):
                break
            if found_start:
                _id, right = line.split(None, 1)
                try:
                    name, status = right.rsplit(None, 1)
                except ValueError:
                    raise SkipException("Incorrect line: '{0}'".format(line))
                self.data.append({
                    "id": _id.strip(),
                    "name": name.strip(),
                    "status": status.strip()})
            if not found_start:
                found_start = line.startswith("repo id")
        if not self.data:
            raise SkipException('No repolist.')
        self.repos = dict((d['id'], d) for d in self.data)

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
        return [i.split('/')[0].lstrip('!')
                for i in self.repos
                if i.startswith(('!rhel', 'rhel'))]
