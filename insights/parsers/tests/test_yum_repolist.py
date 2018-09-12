from insights.parsers import yum
from insights.parsers.yum import YumRepoList
from insights.parsers import SkipException
from insights.tests import context_wrap
import doctest
import pytest

YUM_REPOLIST_CONTENT = """
Loaded plugins: product-id, search-disabled-repos, subscription-manager
repo id                                         repo name                status
rhel-7-server-rpms/7Server/x86_64               Red Hat Enterprise Linux 10415
rhel-7-server-satellite-6.1-rpms/x86_64         Red Hat Satellite 6.1 (f   660
rhel-7-server-satellite-capsule-6.1-rpms/x86_64 Red Hat Satellite Capsul   265
rhel-server-rhscl-7-rpms/7Server/x86_64         Red Hat Software Collect  4571
repolist: 15911

""".strip()

YUM_REPOLIST_CONTENT_EUS = """
Loaded plugins: product-id, rhnplugin, security, subscription-manager
Updating certificate-based repositories.
repo id                              repo name                            status
clone-6u5-server-x86_64              clone-6u5-server-x86_64              3,787
rhel-x86_64-server-6.2.aus           Red Hot Enterprise Linu              5,509
repolist: 3,787

""".strip()

YUM_REPOLIST_CONTENT_MISSING_STATUS = """
Loaded plugins: product-id, rhnplugin, security, subscription-manager
Updating certificate-based repositories.
repo id                              repo name                            status
clone-6u5-server-x86_64              clone-6u5-server-x86_64
"""

YUM_REPOLIST_CONTENT_OUT_OF_DATE = """
Loaded plugins: product-id, search-disabled-repos, subscription-manager
Repodata is over 2 weeks old. Install yum-cron? Or run: yum makecache fast
repo id                              repo name                                          status
!rhel-7-server-extras-rpms/x86_64    Red Hat Enterprise Linux 7 Server - Extras (RPMs)  877
!rhel-7-server-rpms/7Server/x86_64   Red Hat Enterprise Linux 7 Server (RPMs)           20,704
repolist: 21,581
"""

YUM_REPOLIST_DOC = """
Loaded plugins: langpacks, product-id, search-disabled-repos, subscription-manager
repo id                                             repo name                                                                                                    status
rhel-7-server-e4s-rpms/x86_64                       Red Hat Enterprise Linux 7 Server - Update Services for SAP Solutions (RPMs)                                 12,250
rhel-ha-for-rhel-7-server-e4s-rpms/x86_64           Red Hat Enterprise Linux High Availability (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)         272
rhel-ha-for-rhel-7-server-rpms/x86_64               Red Hat Enterprise Linux High Availability (for RHEL 7 Server) (RPMs)                                           225
rhel-sap-hana-for-rhel-7-server-e4s-rpms/x86_64     RHEL for SAP HANA (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)                                   21
repolist: 12,768
"""


def test_yum_repolist():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT))
    assert len(repo_list) == 4
    assert repo_list[0] == {"id": "rhel-7-server-rpms/7Server/x86_64",
                            "name": "Red Hat Enterprise Linux",
                            "status": "10415"}
    assert 'rhel-7-server-rpms/7Server/x86_64' in repo_list
    assert repo_list['rhel-7-server-rpms/7Server/x86_64'] == repo_list[0]
    assert repo_list.eus == []


def test_eus():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_EUS))
    assert len(repo_list) == 2
    assert repo_list[0] == {"id": "clone-6u5-server-x86_64",
                            "name": "clone-6u5-server-x86_64",
                            "status": "3,787"}
    assert repo_list.eus == ["6.2.aus"]


def test_rhel_repos():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT))
    assert len(repo_list.rhel_repos) == 4
    assert set(repo_list.rhel_repos) == set(['rhel-7-server-rpms',
                                             'rhel-7-server-satellite-6.1-rpms',
                                             'rhel-7-server-satellite-capsule-6.1-rpms',
                                             'rhel-server-rhscl-7-rpms'])


def test_rhel_repos_missing_status():
    with pytest.raises(SkipException) as se:
        YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_MISSING_STATUS))
    assert 'Incorrect line:' in str(se)


def test_rhel_repos_empty():
    with pytest.raises(SkipException) as se:
        YumRepoList(context_wrap(''))
    assert 'No repolist.' in str(se)


def test_rhel_repos_out_of_date():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_OUT_OF_DATE))
    assert len(repo_list) == 2
    assert set(repo_list.rhel_repos) == set(['rhel-7-server-extras-rpms',
                                             'rhel-7-server-rpms'])


def test_invalid_get_type():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT))
    assert repo_list[YumRepoList] is None


def test_doc_examples():
    env = {
            'repolist': YumRepoList(context_wrap(YUM_REPOLIST_DOC)),
          }
    failed, total = doctest.testmod(yum, globs=env)
    assert failed == 0
