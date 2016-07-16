from falafel.core.plugins import mapper
import re

"""
Parse the output of command "docker_list_images" and "docker_list_" and return dict.
Example:

Output of command "/usr/bin/docker images --all --no-trunc --digests":
REPOSITORY                           TAG                 DIGEST              IMAGE ID                                                           CREATED             VIRTUAL SIZE
rhel7_imagemagick                    latest              <none>              882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2   4 days ago          785.4 MB
rhel6_nss-softokn                    latest              <none>              dd87dad2c7841a19263ae2dc96d32c501ee84a92f56aed75bb67f57efe4e48b5   5 days ago          449.7 MB

Content of dict:
[{"REPOSITORY":"rhel7_imagemagick", "TAG":"latest", "DIGEST":"<none>", "IMAGE ID":"882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2", "CREATED":"4 days ago", "VIRTUAL SIZE":"785.4 MB"}, {"REPOSITORY":"rhel6_nss-softokn", "TAG":"latest", "DIGEST":"<none>", "IMAGE ID":"dd87dad2c7841a19263ae2dc96d32c501ee84a92f56aed75bb67f57efe4e48b5", "CREATED":"5 days ago", "VIRTUAL SIZE":"449.7 MB"}]


Output of command "/usr/bin/docker ps --all --no-trunc --size":
CONTAINER ID                                                       IMAGE                                                              COMMAND                                            CREATED             STATUS                        PORTS                  NAMES               SIZE
95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102   bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478   "/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"   51 minutes ago      Exited (137) 50 minutes ago                          tender_rosalind     4.751 MB (virtual 200.4 MB)
03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216   rhel7_httpd                                                        "/usr/sbin/httpd -DFOREGROUND"                     45 seconds ago      Up 37 seconds                 0.0.0.0:8080->80/tcp   angry_saha          796 B (virtual 669.2 MB)

Content of dict:
[{"CONTAINER ID":"95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102", "IMAGE":"bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478", "COMMAND":'"/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"', "CREATED": "51 minutes ago", "STATUS":"Exited (137) 50 minutes ago", "PORTS":"None", "NAMES":"tender_rosalind", "SIZE":"4.751 MB (virtual 200.4 MB)"},{"CONTAINER ID":"03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216", "IMAGE":"rhel7_httpd", "COMMAND":'"/usr/sbin/httpd -DFOREGROUND"', "CREATED": "45 seconds ago", "STATUS":"Up 37 seconds", "PORTS":"0.0.0.0:8080->80/tcp", "NAMES":"angry_saha", "SIZE":"796 B (virtual 669.2 MB)"}]
"""

list_image_headers = ["REPOSITORY", "TAG", "DIGEST", "IMAGE ID", "CREATED", "VIRTUAL SIZE"]
list_container_headers = ["CONTAINER ID", "IMAGE", "COMMAND", "CREATED", "STATUS", "PORTS", "NAMES", "SIZE"]


@mapper("docker_list_images")
def docker_list_images_parser(context):
    return [dict(zip(list_image_headers, re.split(r'\s{3,}', row))) for row in context.content[1:]]


@mapper("docker_list_containers")
def docker_list_containers_parser(context):
    docker_containers_list = []
    for row in context.content[1:]:
        result = re.split(r'\s{3,}', row)
        if len(result) == 7:
            result.insert(5, None)
        docker_containers_list.append(dict(zip(list_container_headers, result)))
    return docker_containers_list
