from falafel.mappers import docker_list
from falafel.tests import context_wrap

DOCKER_LIST_IMAGES = """
REPOSITORY                           TAG                 DIGEST              IMAGE ID                                                           CREATED             VIRTUAL SIZE
rhel6_vsftpd                         latest              <none>              412b684338a1178f0e5ad68a5fd00df01a10a18495959398b2cf92c2033d3d02   37 minutes ago      459.5 MB
<none>                               <none>              <none>              34c167d900afb820ecab622a214ce3207af80ec755c0dcb6165b425087ddbc3a   5 days ago          205.3 MB
<none>                               <none>              <none>              76e65756ff110ca5ea54ac02733fe04301b33a9190689eb524dd5aa18843996a   5 days ago          205.3 MB
""".strip()

DOCKER_LIST_CONTAINERS = """
CONTAINER ID                                                       IMAGE                                                              COMMAND                                            CREATED             STATUS                      PORTS                  NAMES               SIZE
03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216   rhel7_httpd                                                        "/usr/sbin/httpd -DFOREGROUND"                     45 seconds ago      Up 37 seconds               0.0.0.0:8080->80/tcp   angry_saha          796 B (virtual 669.2 MB)
95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102   bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478   "/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"   18 hours ago        Exited (137) 18 hours ago                          tender_rosalind     4.751 MB (virtual 200.4 MB)
""".strip()

class Testdockerlist():
    def test_docker_list_images(self):
        result = docker_list.docker_list_images_parser(context_wrap(DOCKER_LIST_IMAGES))
        assert result[0].get("REPOSITORY") == "rhel6_vsftpd"
        assert result[0].get("CREATED")  == "37 minutes ago"
        assert result[0].get("VIRTUAL SIZE") == "459.5 MB"
        assert result[1].get("REPOSITORY") == "<none>"
        assert result[1].get("TAG") == "<none>"
    def test_docker_list_containers(self):
        result = docker_list.docker_list_containers_parser(context_wrap(DOCKER_LIST_CONTAINERS))
        assert result[0].get("CONTAINER ID") == "03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216"
        assert result[0].get("COMMAND") == '"/usr/sbin/httpd -DFOREGROUND"'
        assert result[1].get("COMMAND") == '"/bin/sh -c \'yum install -y vsftpd-2.2.2-6.el6\'"'
        assert result[0].get("CREATED") == "45 seconds ago"
        assert result[0].get("PORTS") == "0.0.0.0:8080->80/tcp"
        assert result[1].get("PORTS") == None
        assert result[0].get("SIZE") == "796 B (virtual 669.2 MB)"




