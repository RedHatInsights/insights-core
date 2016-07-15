GLOBAL_PRODUCTS = []
PRODUCT_NAMES = []
DEFAULT_VERSION = ["-1", "-1"]


def product(klass):
    GLOBAL_PRODUCTS.append(klass)
    PRODUCT_NAMES.append(klass.name)
    return klass


def get_system(metadata, hostname):
    for system in metadata.get("systems", []):
        if system.get("system_id") == hostname:
            return system


class MultiNodeProduct(object):

    def __init__(self, role=None):
        self.role = role

    def __nonzero__(self):
        return bool(self.role)

    def is_parent(self):
        return self.role == self.parent_type

    @classmethod
    def from_metadata(cls, metadata, hostname):
        instance = cls()
        current_system = get_system(metadata, hostname)
        if metadata.get("product", "").lower() == cls.name and current_system:
            instance.__dict__ = current_system
            if hasattr(instance, "type"):
                instance.role = instance.type
        return instance


@product
class Docker(MultiNodeProduct):

    name = "docker"
    parent_type = "host"


@product
class OSP(MultiNodeProduct):

    name = "osp"
    parent_type = "Director"


@product
class RHEV(MultiNodeProduct):

    name = "rhev"
    parent_type = "Manager"


@product
class RHEL(object):

    name = "rhel"

    def __init__(self, version=DEFAULT_VERSION, release=None):
        self.version = version
        self.release = release

    def __nonzero__(self):
        return all([(self.version != DEFAULT_VERSION),
                   bool(self.release)])

    @classmethod
    def from_metadata(cls, metadata, processor_obj):
        return cls()


class Context(object):

    def __init__(self, **kwargs):
        self.version = kwargs.pop("version", DEFAULT_VERSION)
        self.metadata = kwargs.pop("metadata", {})
        optional_attrs = [
            "content", "path", "hostname", "release", "machine_id", "target"]
        for k in optional_attrs:
            setattr(self, k, kwargs.pop(k, None))

        for p in GLOBAL_PRODUCTS:
            if p.name in kwargs:
                setattr(self, p.name, kwargs.pop(p.name))
            else:
                setattr(self, p.name, p.from_metadata(self.metadata, self.hostname))

    def product(self):
        for pname in PRODUCT_NAMES:
            if getattr(self, pname):
                return getattr(self, pname)

    def __repr__(self):
        return repr(dict((k, str(v)[:30]) for k, v in self.__dict__.items()))
