from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed, marshalling


def _metadata(context, product_filter=None):
    if (not product_filter) or filter(lambda line: product_filter in line, context.content):
        try:
            md = marshalling.unmarshal("\n".join(context.content))
            product = md["product"]
            if "links" in md:
                product += "Child"
            return globals()[product](md)
        except:
            pass


@mapper("metadata.json")
def metadata(context):
    return _metadata(context)


@mapper("metadata.json")
def rhev(context):
    return _metadata(context, MultinodeMetadata.RHEV)


@mapper("metadata.json")
def docker(context):
    return _metadata(context, MultinodeMetadata.DOCKER)


@mapper("metadata.json")
def osp(context):
    return _metadata(context, MultinodeMetadata.OSP)


class MultinodeMetadata(MapperOutput):

    RHEV = "RHEV"
    DOCKER = "Docker"
    OSP = "OSP"

    common_fields = ["display_name", "insights_version"]
    fields = []

    def __init__(self, data, path=None):
        self.data = data
        for f in self.common_fields:
            setattr(self, f, data.get(f))
        for f in self.fields:
            setattr(self, f, data.get(f))

    @computed
    def product(self):
        return self.data["product"]

    @property
    def children(self):
        if not hasattr(self, "children"):
            self.children = self.populate_children()
        return self.children.values()

    def child(self, system_id):
        if not hasattr(self, "children"):
            self.children = self.populate_children()
        return self.children.get(system_id)

    def child_class(self):
        return globals()[self.__class__.__name__ + "Child"]

    def populate_children(self):
        children = {}
        for child in self.data["systems"]:
            children[child["system_id"]] = self.child_class()(child, parent=self)
        return children

    @classmethod
    def products(cls):
        return [cls.RHEV, cls.DOCKER, cls.OSP]


class RHEV(MultinodeMetadata):

    fields = [
        "storagedomains", "hosts", "api_version",
        "datacenters", "networks", "rhev_version",
        "coordinator_version", "diskprofiles", "vms",
        "clusters"
    ]


class Docker(MultinodeMetadata):
    pass


class OSP(MultinodeMetadata):

    fields = [
        "nova_client_api_version", "coordinator_version",
        "rhel_version", "rhosp_version"
    ]


class MultinodeChild(MultinodeMetadata):

    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent
        for f in self.fields:
            setattr(self, f, data.get(f))

    @property
    def role(self):
        return self.data["type"]


class OSPChild(MultinodeChild):

    fields = [
        "status", "ip"
    ]


class RHEVChild(MultinodeChild):
    pass


class DockerChild(MultinodeChild):

    @property
    def image(self):
        return self.data["type"] == "image"

    @property
    def host(self):
        return self.data["type"] == "host"

    @property
    def container(self):
        return self.data["type"] == "container"
