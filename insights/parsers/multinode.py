from ..core import dr
from .. import metadata


class MultinodeMetaclass(type):
    def __init__(cls, name, bases, dct):
        if name != 'MultinodeMetadata' and not name.endswith("Child"):
            cls.products.append(name)
        super(MultinodeMetaclass, cls).__init__(name, bases, dct)


class MultinodeMetadata(object):
    __metaclass__ = MultinodeMetaclass
    products = []

    common_fields = ["display_name", "insights_version"]
    fields = []

    def __init__(self, data, path=None):
        if data['product'] != self.__class__.__name__:
            raise dr.SkipComponent()
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

    def populate_children(self):
        children = {}
        for child in self.data["systems"]:
            children[child["system_id"]] = self.child_class(child, parent=self)
        return children


@metadata(group=dr.GROUPS.cluster)
def rhev(data):
    return RHEV(data)


@metadata(group=dr.GROUPS.cluster)
class RHEV(MultinodeMetadata):
    fields = [
        "storagedomains", "hosts", "api_version",
        "datacenters", "networks", "rhev_version",
        "coordinator_version", "diskprofiles", "vms",
        "clusters"
    ]

    @property
    def child_class(self):
        return RHEVChild


@metadata(group=dr.GROUPS.cluster)
def docker(data):
    return Docker(data)


@metadata(group=dr.GROUPS.cluster)
class Docker(MultinodeMetadata):
    @property
    def child_class(self):
        return DockerChild


@metadata(group=dr.GROUPS.cluster)
def osp(data):
    return OSP(data)


@metadata(group=dr.GROUPS.cluster)
class OSP(MultinodeMetadata):
    fields = [
        "nova_client_api_version", "coordinator_version",
        "rhel_version", "rhosp_version"
    ]

    @property
    def child_class(self):
        return OSPChild


class MultinodeChild(MultinodeMetadata):
    __metaclass__ = type

    def __init__(self, data, parent=None):
        if data['product'] != self.parent_class.__name__ or "links" not in data:
            raise dr.SkipComponent()
        self.data = data
        self.parent = parent
        for f in self.fields:
            setattr(self, f, data.get(f))

    @property
    def role(self):
        return self.data["type"]


@metadata()
class OSPChild(MultinodeChild):
    fields = [
        "status", "ip"
    ]
    parent_class = OSP


@metadata()
class RHEVChild(MultinodeChild):
    parent_class = RHEV


@metadata()
class DockerChild(MultinodeChild):
    parent_class = Docker

    @property
    def image(self):
        return self.data["type"] == "image"

    @property
    def host(self):
        return self.data["type"] == "host"

    @property
    def container(self):
        return self.data["type"] == "container"
