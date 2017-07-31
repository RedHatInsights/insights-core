import logging
from insights.util.subproc import call
from subprocess import STDOUT

log = logging.getLogger(__name__)
GLOBAL_PRODUCTS = []
PRODUCT_NAMES = []
DEFAULT_VERSION = ["-1", "-1"]

FSRoots = []


def fs_root(thing):
    FSRoots.append(thing)
    return thing


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
            "content", "path", "hostname", "release",
            "machine_id", "target", "last_client_run"
        ]
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


class ExecutionContext(object):
    def __init__(self, timeout=None):
        self.timeout = timeout

    def check_output(self, cmd, timeout=None):
        """ Subclasses can override to provide special
            environment setup, command prefixes, etc.
        """
        return call(cmd, timeout=timeout or self.timeout, stderr=STDOUT)

    def shell_out(self, cmd, split=True, timeout=None):
        output = self.check_output(cmd, timeout=timeout)

        if split:
            return [l.rstrip() for l in output.splitlines()]
        return output


@fs_root
class HostContext(ExecutionContext):
    def __init__(self, hostname, root="/", timeout=None):
        super(HostContext, self).__init__(timeout)
        self.hostname = hostname
        self.root = root


# No fs_root here. Dependence on this context should be explicit.
class DockerHostContext(HostContext):
    pass


@fs_root
class FileArchiveContext(ExecutionContext):
    def __init__(self, root, paths, stored_command_prefix="insights_commands"):
        self.root = root
        self.paths = paths
        self.stored_command_prefix = stored_command_prefix
        super(FileArchiveContext, self).__init__()


@fs_root
class ClusterArchiveContext(ExecutionContext):
    def __init__(self, root, paths, stored_command_prefix="insights_commands"):
        self.root = root
        self.paths = paths
        self.stored_command_prefix = stored_command_prefix
        super(FileArchiveContext, self).__init__()


@fs_root
class DockerImageContext(ExecutionContext):
    def __init__(self, root):
        super(DockerImageContext, self).__init__()
        self.root = root


class OpenStackContext(ExecutionContext):
    def __init__(self, hostname):
        super(OpenStackContext, self).__init__()
        self.hostname = hostname


class OpenShiftContext(ExecutionContext):
    def __init__(self, hostname):
        super(OpenShiftContext, self).__init__()
        self.hostname = hostname
