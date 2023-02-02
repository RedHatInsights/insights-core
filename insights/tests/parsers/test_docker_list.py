import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import docker_list
from insights.tests import context_wrap


DOCKER_LIST_IMAGES = """
REPOSITORY                           TAG                 DIGEST              IMAGE ID                                                           CREATED             VIRTUAL SIZE
rhel6_vsftpd                         latest              <none>              412b684338a1178f0e5ad68a5fd00df01a10a18495959398b2cf92c2033d3d02   37 minutes ago      459.5 MB
rhel7_imagemagick                    latest              <none>              882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2   4 days ago          785.4 MB
rhel6_nss-softokn                    latest              <none>              dd87dad2c7841a19263ae2dc96d32c501ee84a92f56aed75bb67f57efe4e48b5   5 days ago          449.7 MB
<none>                               <none>              <none>              34c167d900afb820ecab622a214ce3207af80ec755c0dcb6165b425087ddbc3a   5 days ago          205.3 MB
""".strip()

DOCKER_LIST_CONTAINERS = """
CONTAINER ID                                                       IMAGE                                                              COMMAND                                            CREATED             STATUS                      PORTS                  NAMES               SIZE
03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216   rhel7_httpd                                                        "/usr/sbin/httpd -DFOREGROUND"                     45 seconds ago      Up 37 seconds               0.0.0.0:8080->80/tcp   angry_saha          796 B (virtual 669.2 MB)
95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102   bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478   "/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"   18 hours ago        Exited (137) 18 hours ago                          tender_rosalind     4.751 MB (virtual 200.4 MB)
""".strip()

DOCKER_LIST_IMAGES_NO_DATA = """
REPOSITORY                           TAG                 DIGEST              IMAGE ID                                                           CREATED             VIRTUAL SIZE
"""

DOCKER_HELP_OUTPUT = """
/usr/bin/docker - version 1.5

Usage: /usr/bin/docker [OPTIONS]

Options:
  -help             Show this help.
"""


def test_docker_list_images():
    result = docker_list.DockerListImages(context_wrap(DOCKER_LIST_IMAGES))
    # All rows get read:
    assert len(result.rows) == 4
    # Rows with data are as normal
    assert result.rows[0].get("REPOSITORY") == "rhel6_vsftpd"
    assert result.rows[0].get("TAG") == "latest"
    assert result.rows[0].get("DIGEST") == "<none>"
    assert result.rows[0].get("IMAGE ID") == '412b684338a1178f0e5ad68a5fd00df01a10a18495959398b2cf92c2033d3d02'
    assert result.rows[0].get("CREATED") == "37 minutes ago"
    assert result.rows[0].get("VIRTUAL SIZE") == "459.5 MB"
    # Rows with <none> still get processed.
    assert result.rows[3].get("REPOSITORY") == "<none>"
    assert result.rows[1].get("TAG") == "latest"
    assert result.rows[3].get("IMAGE ID") == '34c167d900afb820ecab622a214ce3207af80ec755c0dcb6165b425087ddbc3a'
    assert result.rows[2].get("REPOSITORY") == "rhel6_nss-softokn"
    assert result.rows[2].get("TAG") == "latest"
    assert result.rows[2].get("IMAGE ID") == 'dd87dad2c7841a19263ae2dc96d32c501ee84a92f56aed75bb67f57efe4e48b5'

    assert result.data['rhel6_vsftpd']['CREATED'] == '37 minutes ago'
    # Same data in both accessors
    assert result.data['rhel6_vsftpd'] == result.rows[0]
    # Can't list repositories if they don't have a repository name
    assert '<none>' not in result.data


def test_docker_list_containers():
    result = docker_list.DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS))
    assert len(result.rows) == 2
    assert result.rows[0].get("CONTAINER ID") == "03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216"
    assert result.rows[0].get("COMMAND") == '"/usr/sbin/httpd -DFOREGROUND"'
    assert result.rows[0].get("SIZE") == "796 B (virtual 669.2 MB)"
    assert result.rows[0].get("CREATED") == "45 seconds ago"
    assert result.rows[0].get("PORTS") == "0.0.0.0:8080->80/tcp"
    assert result.rows[1].get("CONTAINER ID") == "95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102"
    assert result.rows[1].get("COMMAND") == '"/bin/sh -c \'yum install -y vsftpd-2.2.2-6.el6\'"'
    assert result.rows[1]['STATUS'] == 'Exited (137) 18 hours ago'
    assert result.rows[1].get("PORTS") == ''

    assert sorted(result.data.keys()) == sorted(['angry_saha', 'tender_rosalind'])
    assert result.data['angry_saha'] == result.rows[0]
    assert result.data['tender_rosalind'] == result.rows[1]


def test_docker_list_images_no_data():
    with pytest.raises(SkipComponent) as ex:
        docker_list.DockerListImages(context_wrap(DOCKER_LIST_IMAGES_NO_DATA))
    assert 'No data.' in str(ex)


def test_docker_list_images_help_output():
    with pytest.raises(SkipComponent) as ex:
        docker_list.DockerListImages(context_wrap(DOCKER_HELP_OUTPUT))
    assert 'No data only help output.' in str(ex)

    with pytest.raises(SkipComponent) as ex:
        docker_list.DockerListContainers(context_wrap(DOCKER_HELP_OUTPUT))
    assert 'No data only help output.' in str(ex)


def test_undefined_key_field():
    with pytest.raises(NotImplementedError):
        assert docker_list.DockerList(context_wrap(DOCKER_LIST_CONTAINERS)).key_field is None


def test_documentation():
    failed_count, tests = doctest.testmod(
        docker_list,
        globs={'images': docker_list.DockerListImages(context_wrap(DOCKER_LIST_IMAGES)),
               'containers': docker_list.DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS))}
    )
    assert failed_count == 0
