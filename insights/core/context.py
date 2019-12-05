import logging
import os
import six
from contextlib import contextmanager
from insights.util import streams, subproc

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

    def __bool__(self):
        return bool(self.role)

    __nonzero__ = __bool__

    def is_parent(self):
        return self.role == self.parent_type


def create_product(metadata, hostname):
    current_system = get_system(metadata, hostname)
    for p in GLOBAL_PRODUCTS:
        if metadata.get("product", "").lower() == p.name and current_system:
            instance = p()
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

    def __bool__(self):
        return all([(self.version != DEFAULT_VERSION),
                   bool(self.release)])

    __nonzero__ = __bool__

    @classmethod
    def from_metadata(cls, metadata, processor_obj):
        return cls()


class Context(object):
    def __init__(self, **kwargs):
        self.version = kwargs.pop("version", DEFAULT_VERSION)
        self.metadata = kwargs.pop("metadata", {})
        self.loaded = True
        self.cmd = None
        optional_attrs = [
            "content", "path", "hostname", "release",
            "machine_id", "target", "last_client_run", "relative_path"
        ]
        for k in optional_attrs:
            setattr(self, k, kwargs.pop(k, None))

        self.relative_path = self.path

        for p in GLOBAL_PRODUCTS:
            if p.name in kwargs:
                setattr(self, p.name, kwargs.pop(p.name))
            else:
                setattr(self, p.name, create_product(self.metadata, self.hostname))

    def stream(self):
        return iter(self.content)

    def product(self):
        for pname in PRODUCT_NAMES:
            if hasattr(self, pname):
                return getattr(self, pname)

    def __repr__(self):
        return repr(dict((k, str(v)[:30]) for k, v in self.__dict__.items()))


class ExecutionContextMeta(type):
    registry = []

    def __init__(cls, name, bases, dct):
        if name == "ExecutionContext":
            return
        ExecutionContextMeta.registry.append(cls)

    @classmethod
    def identify(cls, files):
        for e in reversed(cls.registry):
            root, ctx = e.handles(files)
            if ctx is not None:
                return (root, ctx)
        return (None, None)


class ExecutionContext(six.with_metaclass(ExecutionContextMeta)):
    marker = None

    def __init__(self, root="/", timeout=None, all_files=None):
        self.root = root
        self.timeout = timeout
        self.all_files = all_files or []

    @classmethod
    def handles(cls, files):
        if cls.marker is None or not files:
            return (None, None)

        sep = os.path.sep
        m = sep + cls.marker.lstrip(sep)
        for f in files:
            if m in f:
                i = f.find(m)
                if f.endswith(m) or f[i + len(m)] == sep:
                    root = os.path.dirname(f[:i + 1])
                    return root, cls
        return (None, None)

    def check_output(self, cmd, timeout=None, keep_rc=False, env=None):
        """ Subclasses can override to provide special
            environment setup, command prefixes, etc.
        """
        return subproc.call(cmd, timeout=timeout or self.timeout,
                keep_rc=keep_rc, env=env)

    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None):
        env = env or os.environ
        rc = None
        raw = self.check_output(cmd, timeout=timeout, keep_rc=keep_rc, env=env)
        if keep_rc:
            rc, output = raw
        else:
            output = raw

        if split:
            output = output.splitlines()

        return (rc, output) if keep_rc else output

    @contextmanager
    def stream(self, *args, **kwargs):
        with streams.stream(*args, **kwargs) as s:
            yield s

    @contextmanager
    def connect(self, *args, **kwargs):
        with streams.connect(*args, **kwargs) as s:
            yield s

    def locate_path(self, path):
        return os.path.expandvars(path)

    def __repr__(self):
        msg = "<%s('%s', %s)>"
        return msg % (self.__class__.__name__, self.root, self.timeout)


@fs_root
class HostContext(ExecutionContext):
    def __init__(self, root='/', timeout=30, all_files=None):
        super(HostContext, self).__init__(root=root, timeout=timeout, all_files=all_files)


@fs_root
class SerializedArchiveContext(ExecutionContext):
    marker = "insights_archive.txt"


@fs_root
class HostArchiveContext(ExecutionContext):
    marker = "insights_commands"


@fs_root
class SosArchiveContext(ExecutionContext):
    marker = "sos_commands"


@fs_root
class ClusterArchiveContext(ExecutionContext):
    pass


@fs_root
class DockerImageContext(ExecutionContext):
    pass


@fs_root
class JBossContext(HostContext):
    pass


@fs_root
class JDRContext(ExecutionContext):
    marker = "JBOSS_HOME"

    def locate_path(self, path):
        p = path.replace("$JBOSS_HOME", "JBOSS_HOME")
        return super(JDRContext, self).locate_path(p)


@fs_root
class InsightsOperatorContext(ExecutionContext):
    """Recognizes insights-operator archives"""
    marker = "config/featuregate"


@fs_root
class MustGatherContext(ExecutionContext):
    """Recognizes must-gather archives"""
    marker = "namespaces"


class OpenStackContext(ExecutionContext):
    def __init__(self, hostname):
        super(OpenStackContext, self).__init__()
        self.hostname = hostname


class OpenShiftContext(ExecutionContext):
    def __init__(self, hostname):
        super(OpenShiftContext, self).__init__()
        self.hostname = hostname
