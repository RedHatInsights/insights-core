import logging
import six

from contextlib import contextmanager
from insights.util import fs, streams, subproc
from os import environ
from os.path import dirname, exists, expandvars, join, sep

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
            "machine_id", "target", "last_client_run", "relative_path",
            "args"
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

    # Remember that contexts are tried *in reverse order* so that they
    # may be overridden by just loading a plugin.
    @classmethod
    def identify(cls, files):
        for e in reversed(cls.registry):
            root, ctx = e.handles(files)
            if ctx is not None:
                return (root, ctx)
        return (None, None)


class ExecutionContext(six.with_metaclass(ExecutionContextMeta)):
    # A marker is a file path to search for in the archive, or host filesystem.
    # This should be the default path to search for, any additional paths should
    # be defined in extra_markers.
    marker = None
    # Markers is a list of additional file paths to search the archive or host filesystem.
    extra_markers = []
    # Roots is a list of root file paths based on a found marker defined in extra_markers.
    roots = []

    def __init__(self, root="/", timeout=None, all_files=None):
        self.root = root
        self.timeout = timeout
        self.all_files = all_files or []

    @staticmethod
    def _find_marker_roots(m, files):
        """
        Find all the root directories in files that contain the marker file.

        Args:
            m (str): Marker string to search files for.
            files (lst): List of files from an archive or host
                to search for the marker in.

        Returns:
            lst: List of all file paths with the marker found in them.
        """
        marker_roots = set()
        for f in files:
            if m in f:
                i = f.find(m)

                if f.endswith(m) or f[i + len(m)] == sep:
                    root = dirname(f[: i + 1])
                    marker_roots.add(root)

        return marker_roots

    def get_root(self, path):
        """
        If self.roots is defined, loop through them and determine if the path exists in the root,
        if it does return that root. If none are found in the roots list return self.root.

        Args:
            path (str): Path to check if it exists in the list of roots.

        Returns:
            str: Path to use as the root.
        """
        if self.roots:
            for r in self.roots:
                # When processing patterns like globs, the full path of the root
                # will be in the path, so remove the root from the path.
                if r in path:
                    path = path.split(r)[-1]

                if exists(join(r, path.lstrip('/'))):
                    return r

        return self.root

    @classmethod
    def handles(cls, files):
        """
        This method determines the root(s) to set based on the marker(s)
        defined and the files passed in.

        Args:
            files (lst): List of files from an archive or host
                to search for the marker in.

        Returns:
            tuple: Returns the determined root and the cls itself, or None, None.
        """
        if cls.marker is None or not files:
            return None, None

        def _find_closest_root(marker):
            m = sep + marker.lstrip(sep)
            marker_root = cls._find_marker_roots(m, files)

            if len(marker_root) == 1:
                return marker_root.pop()

            if len(marker_root) > 1:
                # When more than one marker is found, return the one which is closest to root.
                root = marker_root.pop()
                for left_one in marker_root:
                    if len(left_one) < len(root):
                        root = left_one

                return root

        # If extra_markers are defined loop through them and determine
        # if any roots exists based on the extra_markers and add them to roots.
        if cls.extra_markers:
            for mark in cls.extra_markers:
                closest_root = _find_closest_root(mark)
                if closest_root:
                    cls.roots.append(closest_root)

        closest_root = _find_closest_root(cls.marker)
        if closest_root:
            return closest_root, cls
        else:
            if cls.roots:
                return cls.roots[0], cls

        return None, None

    def check_output(self, cmd, timeout=None, keep_rc=False, env=None, signum=None):
        """Subclasses can override to provide special environment setup, command prefixes, etc."""
        return subproc.call(cmd, timeout=timeout or self.timeout, signum=signum, keep_rc=keep_rc, env=env)

    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        """
        Execute the command and return the output.

        Args:
            cmd (lst): The command with args.
            split (bool): Weather to split the output or not.
            timeout (int): Number of seconds to wait before killing the command.
            keep_rc (bool): Keep the return code or not.
            env (dict): Environment in which to execute commands.
            signum (int): Signal to send the command on timeout.

        Returns:
            A tuple of the rc and output, or just the output depending on keep_rc.
        """
        rc = None
        raw = self.check_output(cmd, timeout=timeout, keep_rc=keep_rc, env=env or environ, signum=signum)
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
        """
        Expand the path if it has any environmental variables in it.

        Args:
            path (str): Path to expand variables in.

        Returns:
            str: The path with the variables expanded.
        """
        return expandvars(path)

    def write(self, cmd, dst, env, keep_rc, signum, timeout):
        """
        Write the command output provided to a file.

        Args:
            cmd (lst): The command with args.
            dst (str): The file path to write the command output to.
            env (dict): Environment in which to execute commands.
            keep_rc (bool): Keep the return code or not.
            signum (int): Signal to send the command on timeout.
            timeout (int): Number of seconds to wait before killing the command.

        Returns:
            The final output of the pipeline.
        """
        fs.ensure_path(dirname(dst))
        if cmd:
            p = subproc.Pipeline(*cmd, timeout=timeout or self.timeout, signum=signum, env=env)
            return p.write(dst, keep_rc=keep_rc)

    def __repr__(self):
        msg = "<%s('%s', %s)>"
        return msg % (self.__class__.__name__, self.root, self.timeout)


@fs_root
class HostContext(ExecutionContext):
    def __init__(self, root='/', timeout=30, all_files=None):
        super(HostContext, self).__init__(root=root, timeout=timeout, all_files=all_files)


@fs_root
class HostArchiveContext(ExecutionContext):
    marker = "insights_commands"


@fs_root
class SerializedArchiveContext(ExecutionContext):
    marker = "insights_archive.txt"


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
    extra_markers = [
        "ceph/namespaces/openshift-storage",
        "cluster-logging/clo/cr",
        "cluster-scoped-resources"
    ]


class OpenStackContext(ExecutionContext):
    def __init__(self, hostname):
        super(OpenStackContext, self).__init__()
        self.hostname = hostname
