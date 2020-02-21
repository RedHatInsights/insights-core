from insights.parsers import yum
from insights.parsers.yum import YumRepoList
from insights.parsers import SkipException, ParseException
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

YUM_REPOLIST_CONTENT_NOPLUGINS = """
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
repolist: 3,787
"""

YUM_REPOLIST_CONTENT_OUT_OF_DATE = """
Loaded plugins: product-id, search-disabled-repos, subscription-manager
Repodata is over 2 weeks old. Install yum-cron? Or run: yum makecache fast
repo id                              repo name                                          status
!rhel-7-server-extras-rpms/x86_64    Red Hat Enterprise Linux 7 Server - Extras (RPMs)  877
!rhel-7-server-rpms/7Server/x86_64   Red Hat Enterprise Linux 7 Server (RPMs)           20,704
repolist: 21,581
"""

YUM_REPOLIST_CONTENT_OUT_OF_DATE_AND_NOT_MATCH_METADATA = """
Loaded plugins: product-id, search-disabled-repos, subscription-manager
Repodata is over 2 weeks old. Install yum-cron? Or run: yum makecache fast
repo id                              repo name                                          status
!rhel-7-server-extras-rpms/x86_64    Red Hat Enterprise Linux 7 Server - Extras (RPMs)  877
*rhel-7-server-rpms/7Server/x86_64   Red Hat Enterprise Linux 7 Server (RPMs)           20,704
repolist: 21,581
"""

YUM_REPO_NO_REPO_NAME = """
Loaded plugins: enabled_repos_upload, package_upload, priorities, product-id,
              : search-disabled-repos, security, subscription-manager
repo id                                                                               status
LME_EPEL_6_x86_64                                                                     26123
LME_HP_-_Software_Delivery_Repository_Firmware_Pack_for_ProLiant_-_6Server_-_Current   1163
LME_HP_-_Software_Delivery_Repository_Scripting_Took_Kit_-_6Server                       17
LME_HP_-_Software_Delivery_Repository_Service_Pack_for_ProLiant_-_6Server_-_Current    1861
LME_HP_-_Software_Delivery_Repository_Smart_Update_Manager_-_6Server                     21
rhel-6-server-optional-rpms                                                           11358
rhel-6-server-rpms                                                                    19753
repolist: 60296
Uploading Enabled Reposistories Report
Plugin "search-disabled-repos" requires API 2.7. Supported API is 2.6.
Loaded plugins: priorities, product-id
""".strip()

YUM_REPOLIST_CONTENT_MISSING_END = """
Loaded plugins: product-id, rhnplugin, security, subscription-manager
Updating certificate-based repositories.
repo id                              repo name                            status
clone-6u5-server-x86_64              clone-6u5-server-x86_64              1234
"""

YUM_REPOLIST_CONTENT_EMPTY = """
repo id                              repo name                            status
"""

YUM_REPOLIST_DOC = """
Loaded plugins: langpacks, product-id, search-disabled-repos, subscription-manager
repo id                                             repo name                                                                                                    status
rhel-7-server-e4s-rpms/x86_64                       Red Hat Enterprise Linux 7 Server - Update Services for SAP Solutions (RPMs)                                 12,250
!rhel-ha-for-rhel-7-server-e4s-rpms/x86_64          Red Hat Enterprise Linux High Availability (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)         272
*rhel-sap-hana-for-rhel-7-server-e4s-rpms/x86_64    RHEL for SAP HANA (for RHEL 7 Server) Update Services for SAP Solutions (RPMs)                                   21
repolist: 12,768
""".strip()

YUM_REPOLIST_DOC_NO_REPONAME = """
Loaded plugins: package_upload, product-id, search-disabled-repos, security, subscription-manager
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
""".strip()


def test_yum_repolist():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT))
    assert len(repo_list) == 4
    assert repo_list[0] == {"id": "rhel-7-server-rpms/7Server/x86_64",
                            "name": "Red Hat Enterprise Linux",
                            "status": "10415"}
    assert 'rhel-7-server-rpms/7Server/x86_64' in repo_list
    assert repo_list['rhel-7-server-rpms/7Server/x86_64'] == repo_list[0]
    assert repo_list.eus == []


def test_yum_repolist_noplugins():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_NOPLUGINS))
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
    with pytest.raises(ParseException) as se:
        YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_MISSING_STATUS))
    assert 'Incorrect line:' in str(se)


def test_rhel_repos_empty():
    with pytest.raises(SkipException) as se:
        YumRepoList(context_wrap(''))
    assert 'No repolist.' in str(se)

    with pytest.raises(SkipException) as se:
        YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_EMPTY))
    assert 'No repolist.' in str(se)


def test_rhel_repos_out_of_date():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_OUT_OF_DATE))
    assert len(repo_list) == 2
    assert set(repo_list.rhel_repos) == set(['rhel-7-server-extras-rpms',
                                             'rhel-7-server-rpms'])


def test_rhel_repos_out_of_date_and_no_match_metadata():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_OUT_OF_DATE_AND_NOT_MATCH_METADATA))
    assert len(repo_list) == 2
    assert 'rhel-7-server-extras-rpms/x86_64' in repo_list
    assert 'rhel-7-server-rpms/7Server/x86_64' in repo_list
    assert "!rhel-7-server-extras-rpms/x86_64" == repo_list['rhel-7-server-extras-rpms/x86_64']['id']
    assert "*rhel-7-server-rpms/7Server/x86_64" == repo_list['rhel-7-server-rpms/7Server/x86_64']['id']


def test_invalid_get_type():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT))
    assert repo_list[YumRepoList] is None


def test_doc_examples():
    env = {
            'repolist': YumRepoList(context_wrap(YUM_REPOLIST_DOC)),
            'repolist_no_reponame': YumRepoList(context_wrap(YUM_REPOLIST_DOC_NO_REPONAME)),
          }
    failed, total = doctest.testmod(yum, globs=env)
    assert failed == 0


def test_repos_without_repo_name():
    repo_list = YumRepoList(context_wrap(YUM_REPO_NO_REPO_NAME))
    assert 7 == len(repo_list)
    assert 2 == len(repo_list.rhel_repos)


def test_repos_without_ends():
    repo_list = YumRepoList(context_wrap(YUM_REPOLIST_CONTENT_MISSING_END))
    assert 1 == len(repo_list)
    assert 0 == len(repo_list.rhel_repos)
