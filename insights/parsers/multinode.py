from ..core import marshalling
from .. import Parser, parser


def _metadata(context, product_filter=None):
    if product_filter is None or filter(lambda line: product_filter in line, context.content):
        try:
            md = marshalling.unmarshal("\n".join(context.content))
            product = md["product"]
            if "links" in md:
                # Parent metadata.json won't have "links" as a top level key
                product += "Child"
            elif "systems" not in md:
                # This case is for single-node systems that have a
                # metadata.json
                return
            return globals()[product](md)
        except:
            pass


@parser("metadata.json")
def metadata(context):
    return _metadata(context)


@parser("metadata.json")
def rhev(context):
    return _metadata(context, MultinodeMetadata.RHEV)


@parser("metadata.json")
def docker(context):
    return _metadata(context, MultinodeMetadata.DOCKER)


@parser("metadata.json")
def osp(context):
    return _metadata(context, MultinodeMetadata.OSP)


class MultinodeMetadata(Parser):

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

    @property
    def product(self):
        return self.data["product"]

    @property
    def children(self):
        if not hasattr(self, "_children"):
            self._children = self.populate_children()
        return self._children.values()

    def child(self, system_id):
        if not hasattr(self, "_children"):
            self._children = self.populate_children()
        return self._children.get(system_id)

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
