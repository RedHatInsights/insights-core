"""
PodmanList - command ``/usr/bin/podman (images|ps)``
====================================================

Parse the output of command "podman_list_images" and "podman_list_containers",
which have very similar formats with the "docker_list_images" and
"docker_list_containers",

For more details, please refer to the
`:class:insights.parsers.docker_list.DockerList`.
"""
from insights import parser
from insights.specs import Specs
from insights.parsers.docker_list import DockerListContainers, DockerListImages


@parser(Specs.podman_list_images)
class PodmanListImages(DockerListImages):
    """
    Handle the list of podman images using the
    `class:insights.parsers.docker_list.DockerListImages` parser class.

    Sample output of command ``podman images --all --no-trunc --digests``::

        REPOSITORY                           TAG                 DIGEST              IMAGE ID                                                           CREATED             SIZE
        rhel6_vsftpd                         latest              <none>              412b684338a1178f0e5ad68a5fd00df01a10a18495959398b2cf92c2033d3d02   37 minutes ago      459.5 MB
        rhel7_imagemagick                    latest              <none>              882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2   4 days ago          785.4 MB
        rhel6_nss-softokn                    latest              <none>              dd87dad2c7841a19263ae2dc96d32c501ee84a92f56aed75bb67f57efe4e48b5   5 days ago          449.7 MB

    Attributes:
        rows (list): List of row dictionaries.
        images (dict): Dictionary keyed on the value of the "REPOSITORY" fileld

    Examples:
        >>> images.rows[0]['REPOSITORY']
        'rhel6_vsftpd'
        >>> images.rows[1]['SIZE']
        '785.4 MB'
        >>> images.images['rhel6_vsftpd']['CREATED']
        '37 minutes ago'
    """
    pass


@parser(Specs.podman_list_containers)
class PodmanListContainers(DockerListContainers):
    """
    Handle the list of podman containers using the
    `class:insights.parsers.docker_list.DockerListContainers` parser class.


    Sample output of command ``podman ps --all --no-trunc --size``::

        CONTAINER ID                                                       IMAGE                                                              COMMAND                                            CREATED             STATUS                        PORTS                  NAMES               SIZE
        03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216   rhel7_httpd                                                        "/usr/sbin/httpd -DFOREGROUND"                     45 seconds ago      Up 37 seconds                 0.0.0.0:8080->80/tcp   angry_saha          796 B (virtual 669.2 MB)
        95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102   bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478   "/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"   51 minutes ago      Exited (137) 50 minutes ago                          tender_rosalind     4.751 MB (virtual 200.4 MB)

    Attributes:
        rows (list): List of row dictionaries.
        containers(dict): Dictionary keyed on the value of the "NAMES" field

    Examples:
        >>> containers.rows[0]['NAMES']
        'angry_saha'
        >>> containers.rows[0]['STATUS']
        'Up 37 seconds'
        >>> containers.containers['tender_rosalind']['STATUS']
        'Exited (137) 18 hours ago'
    """
    pass
