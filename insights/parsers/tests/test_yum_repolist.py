from insights.parsers.yum import YumRepoList
from insights.tests import context_wrap

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


def test_yum_repolist():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT))
    assert len(repo_list) == 4
    assert repo_list[0] == {"id": "rhel-7-server-rpms/7Server/x86_64",
                            "name": "Red Hat Enterprise Linux",
                            "status": "10415"}
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

    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_MISSING_STATUS))
    assert len(repo_list.rhel_repos) == 0

    repo_list = YumRepoList(context_wrap(''))
    assert len(repo_list.rhel_repos) == 0


def test_valueerror_in_parse():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_MISSING_STATUS))
    assert repo_list[0]['name'] == ''


def test_invalid_get_type():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT))
    assert repo_list[YumRepoList] is None
