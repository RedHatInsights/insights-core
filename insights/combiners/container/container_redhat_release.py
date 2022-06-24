from insights.core.plugins import combiner
from insights.parsers.redhat_release import RedhatRelease, DockerRedhatRelease


@combiner([DockerRedhatRelease, RedhatRelease])
class HostContainerRedhatRelease(object):
    def __init__(self, dockerredhatrelease, hostredhatrelease):
        self.data = {}
        if hostredhatrelease:
            self.data["host"] = hostredhatrelease
        if dockerredhatrelease:
            for item in dockerredhatrelease:
                id = item.file_name.split("_")[2]
                self.data[id] = item