from insights.core.plugins import combiner
from insights.combiners.nginx_conf import NginxConfTree, DockerNginxConfTree




@combiner([DockerNginxConfTree, NginxConfTree])
class HostContainerNginxConfTree(object):
    def __init__(self, dockernginxconfs, hostnginxconfs):
        self.data = {}
        if hostnginxconfs:
            self.data["host"] = hostnginxconfs
        if dockernginxconfs:
            for item, value in dockernginxconfs.doc.items():
                self.data[item] = value