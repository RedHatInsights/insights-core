# coding=utf-8
"""
Yum - Commands
==============
Parsers for ``yum`` commands.

This module contains the classes that parse the output of the commands
`yum -C --noplugins repolist`.

YumRepoList - command ``yum -C --noplugins repolist``
-----------------------------------------------------
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import parse_fixed_table
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
    Class for parsing the output of `yum -C --noplugins repolist` command.

    Typical output of the command is::

        repo id                                             repo name                                                                                                    status
        rhel-7-server-e4s-rpms/x86_64                       Red Hat Enterprise Linux 7 Server - Update Services for SAP Solutions (RPMs)                                 12,250
        !rhel-ha-for-rhel-7-server-e4s-rpms/x86_64          Red Hat Enterprise Linux High Availability (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)         272
        *rhel-sap-hana-for-rhel-7-server-e4s-rpms/x86_64    RHEL for SAP HANA (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)                                   21
        repolist: 12,768

    Or sometimes it just outputs repo id and status::

        repo id                                                                               status
        LME_EPEL_6_x86_64                                                                        26123
        LME_FSMLabs_Timekeeper_timekeeper                                                            2
        LME_HP_-_Software_Delivery_Repository_Firmware_Pack_for_ProLiant_-_6Server_-_Current      1163
        LME_HP_-_Software_Delivery_Repository_Scripting_Took_Kit_-_6Server                          17
        LME_HP_-_Software_Delivery_Repository_Service_Pack_for_ProLiant_-_6Server_-_Current       1915
        LME_HP_-_Software_Delivery_Repository_Smart_Update_Manager_-_6Server                        30
        LME_LME_Custom_Product_Mellanox_OFED                                                       114
        LME_LME_Custom_Product_OMD_RPMS                                                             14
        LME_LME_Custom_Product_RPMs                                                                  5
        LME_LME_Custom_Product_SNOW_Repository                                                       2
        rhel-6-server-optional-rpms                                                            10400+1
        rhel-6-server-rpms                                                                    18256+12
        rhel-6-server-satellite-tools-6.2-rpms                                                      55
        repolist: 58096

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
    """
    _no_repo_available_msg_strs = [
        "No repositories available",
        "No hay ningún repositorio disponible",
        "Keine Paketquellen verfügbar",
        "Nessun repository disponibile",
        "Ez dago biltegirik erabilgarri",
        "Walang repositories na magagamit",
        "Няма налични хранилища",
    ]
    _repo_headers = [
        # repo_id, repo_name, repo_id_length, repo_name_length
        ("repo id", "repo name", 7, 9),
        ("id du dépôt", "nom du dépôt", 11, 12),
        ("Paketquellen-ID", "Paketquellen-Name", 15, 17),
        ("id del repositorio", "nombre del repositorio", 18, 22),
        ("id do repo", "nome do repo", 10, 12),
        ("id repo", "nome repo", 7, 9),
        ("identyfikator repozytorium", "nazwa repozytorium", 26, 18),
        ("tároló azonosító", "tároló neve", 16, 11),
        ("Paketquellenkennung", "Paketquellenname", 19, 16),
        ("仓库 id", "仓库名称", 7, 4),
        ("ід. сховища", "назва сховища", 11, 13),
    ]

    def parse_content(self, content):
        if not content:
            raise SkipComponent('No repolist.')

        if content[0].startswith('repolist:'):
            raise SkipComponent('No repolist.')

        for no_repo_available_msg in self._no_repo_available_msg_strs:
            if content[0].startswith(no_repo_available_msg):
                raise SkipComponent('No repolist.')

        trailing_line_prefix = [
                'repolist:',
                'Uploading Enabled',
                'Loaded plugins:',
                'Plugin ',
                'Unable to upload',
        ]

        self.data = []
        self.repos = {}

        # Header table language defaults to english: self._repo_headers[0]
        # Give it a try for table header in other languages when the default one is not found
        error_raised_for_stander_header_repo_id = None
        for header_pair_index, (header_repo_id, header_repo_name, repo_id_len, repo_name_len) in enumerate(self._repo_headers):
            try:
                self.data = parse_fixed_table(
                        content,
                        heading_ignore=[header_repo_id],
                        header_substitute=[(header_repo_id, 'id' + ' ' * (repo_id_len - 2)),
                                            (header_repo_name, 'name' + ' ' * (repo_name_len - 4))],
                        trailing_ignore=trailing_line_prefix,
                        empty_exception=True)
                break
            except ValueError as e:
                # ValueError raised by parse_fixed_table
                # Likely be a unrecognized header_repo_id raised by calc_offset
                if header_pair_index == 0:
                    error_raised_for_stander_header_repo_id = e
                # When the last pair of table header trying fails, end the parsing by raising a error
                if header_pair_index == len(self._repo_headers) - 1:
                    raise ParseException('Failed to parser yum repolist: {0}'.format(
                                    str(error_raised_for_stander_header_repo_id or e)))

        if not self.data:
            raise SkipComponent('No repolist.')

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
        """
        list: list of all the rhel repos and the item is just the repo id without server and arch info.
            For example::

                self.rhel_repos = [
                    'rhel-7-server-e4s-rpms',
                    'rhel-ha-for-rhel-7-server-e4s-rpms',
                    'rhel-sap-hana-for-rhel-7-server-e4s-rpms'
                ]
        """
        return [i.split('/')[0]
                for i in self.repos
                if i.startswith('rhel-') or '-rhel-' in i]
