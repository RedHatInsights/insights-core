from insights.core.plugins import combiner
from insights.parsers.nginx_log import NginxErrorLog, DockerNginxErrorLog


@combiner([DockerNginxErrorLog, NginxErrorLog])
class HostContainerNginxErrorLog(object):
    def __init__(self, dockernginxerrorlog, hostnginxerrorlog):
        self.data = {}
        if hostnginxerrorlog:
            self.data["host"] = hostnginxerrorlog
        if dockernginxerrorlog:
            for item in dockernginxerrorlog:
                id = item.file_name.split("_")[2]
                self.data[id] = item
