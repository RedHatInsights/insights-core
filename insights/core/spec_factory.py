import itertools
import logging
import os
import re
import six
import traceback

from collections import defaultdict
from glob import glob

from insights.core import blacklist, dr
from insights.core.filters import get_filters
from insights.core.context import ExecutionContext, FSRoots, HostContext
from insights.core.plugins import datasource, ContentException, is_datasource
from insights.core.serde import deserializer, serializer
from insights.util import subproc
import shlex

log = logging.getLogger(__name__)


COMMANDS = {}

SAFE_ENV = {
    "PATH": os.path.pathsep.join(["/bin", "/usr/bin", "/sbin", "/usr/sbin"])
}
"""
A minimal set of environment variables for use in subprocess calls
"""


def enc(s):
    escape_encoding = "string_escape" if six.PY2 else "unicode_escape"
    return s.encode(escape_encoding)


def escape(s):
    return re.sub(r"([=\(\)|\-_!@*~\"&/\\\^\$\=])", r"\\\1", s)


def mangle_command(command, name_max=255):
    """
    Mangle a command line string into something suitable for use as the basename of a filename.
    At minimum this function must remove slashes, but it also does other things to clean
    the basename: removing directory names from the command name, replacing many non-
    characters with undersores, in addition to replacing slashes with dots.

    By default, curly braces, '{' and '}', are replaced with underscore, set 'has_variables'
    to leave curly braces alone.

    This function was copied from the function that insights-client uses to create the name it
    to capture the output of the command.

    Here, server side, it is used to figure out what file in the archive contains the output
    a command.  Server side, the command may contain references to variables (names
    matching curly braces) that will be expanded before the name is actually used as a file name.

    To completly mimic the insights-client behavior, curly braces need to be replaced
    underscores.  If the command has variable references, the curly braces must be left alone.
    Set has_variables, to leave curly braces alone.

    This implementation of 'has_variables' assumes that variable names only contain
    that are not replaced by mangle_command.
    """
    pattern = r"[^\w\-\.\/]+"

    mangledname = re.sub(r"^/(usr/|)(bin|sbin)/", "", command)
    mangledname = re.sub(pattern, "_", mangledname)
    mangledname = re.sub(r"/", ".", mangledname).strip(" ._-")
    mangledname = mangledname[:name_max]
    return mangledname


class ContentProvider(object):
    def __init__(self):
        self.cmd = None
        self.args = None
        self.rc = None
        self.path = None
        self.relative_path = None
        self._content = None
        self._exception = None

    def load(self):
        raise NotImplemented()

    @property
    def content(self):
        if self._exception:
            raise self._exception

        if self._content is None:
            try:
                self._content = self.load()
            except Exception as ex:
                self._exception = ex
                raise

        return self._content

    def __repr__(self):
        msg = "<%s(path=%s, cmd=%s)>"
        return msg % (self.__class__.__name__, self.path or "", self.cmd or "")

    def __unicode__(self):
        return self.__repr__()

    def __str__(self):
        return self.__unicode__()


class FileProvider(ContentProvider):
    def __init__(self, relative_path, root="/", ds=None):
        super(FileProvider, self).__init__()
        self.root = root
        self.relative_path = relative_path.lstrip("/")

        self.path = os.path.join(root, self.relative_path)
        self.file_name = os.path.basename(self.path)

        self.ds = ds
        self.validate()

    def validate(self):
        if not blacklist.allow_file("/" + self.relative_path):
            raise dr.SkipComponent()

        if not os.path.exists(self.path):
            raise ContentException("%s does not exist." % self.path)

        if os.path.islink(self.path):
            resolved = os.path.realpath(self.path)
            if not resolved.startswith(self.root):
                msg = "Symbolic link points outside archive: %s -> %s."
                raise Exception(msg % (self.path, resolved))

        if not os.access(self.path, os.R_OK):
            raise ContentException("Cannot access %s" % self.path)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.path)


class RawFileProvider(FileProvider):
    """
    Class used in datasources that returns the contents of a file a single
    string. The file is not filtered.
    """

    def load(self):
        with open(self.path, 'rb') as f:
            return f.read()


class TextFileProvider(FileProvider):
    """
    Class used in datasources that returns the contents of a file a list of
    lines. Each line is filtered if filters are defined for the datasource.
    """

    def load(self):

        filters = False
        if self.ds:
            filters = "\n".join(get_filters(self.ds))
        if filters:
            cmd = [["grep", "-F", filters, self.path]]
            rc, out = subproc.call(cmd, shell=False, keep_rc=True, env=SAFE_ENV)
            if rc == 0 and out != '':
                results = out.splitlines()
            else:
                return []
        else:
            with open(self.path, "rU") as f:
                results = [l.rstrip("\n") for l in f]
        return results


class CommandOutputProvider(ContentProvider):
    """
    Class used in datasources to return output from commands.
    """
    def __init__(self, cmd, ctx, args=None, content=None, rc=None, split=True, keep_rc=False):
        super(CommandOutputProvider, self).__init__()
        self.cmd = cmd
        self.path = os.path.join("insights_commands", mangle_command(cmd))
        self.ctx = ctx
        # args are already interpolated into cmd. They're stored here for context."
        self.args = args
        self._content = content
        self.rc = rc
        self.split = split
        self.keep_rc = keep_rc
        self.validate()

    def validate(self):
        if not blacklist.allow_command(self.cmd):
            raise dr.SkipComponent()

    def load(self):
        if self.keep_rc:
            self.rc, result = self.ctx.shell_out(self.cmd, self.split, keep_rc=True)
            return result
        else:
            return self.ctx.shell_out(self.cmd, self.split)

    def __repr__(self):
        return 'CommandOutputProvider("%s")' % self.cmd


class RegistryPoint(object):
    """
    Marker class for declaring that an element of a `SpecSet` subclass
    is a registry point against which further subclasses can register
    datasource implementations by simply declaring them with the same name.
    """
    def __init__(self, metadata=None, multi_output=False, raw=False):
        self.metadata = metadata
        self.multi_output = multi_output
        self.raw = raw
        self.__name__ = self.__class__.__name__
        datasource([], metadata=metadata, multi_output=multi_output, raw=raw)(self)

    def __call__(self, broker):
        for c in reversed(dr.get_delegate(self).deps):
            if c in broker:
                return broker[c]
        raise dr.SkipComponent()

    def __repr__(self):
        return dr.get_name(self)


class SpecDescriptor(object):
    """
    Descriptor Protocol handler that returns the literal function from a
    class during dot (.) access.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        return self.func

    def __set__(self, obj, val):
        raise AttributeError()


def _get_ctx_dependencies(func):
    ctxs = []
    try:
        for c in dr.get_dependencies(func):
            if issubclass(c, ExecutionContext):
                ctxs.append(c)
    except:
        pass
    return ctxs


def _register_context_handler(parents, func):
    name = func.__name__
    parents = list(itertools.takewhile(lambda x: name in x.registry, parents))
    if not parents:
        return

    ctx_handlers = parents[-1].context_handlers
    for c in _get_ctx_dependencies(func):
        for old in ctx_handlers[name][c]:
            dr.add_ignore(old, c)
        ctx_handlers[name][c].append(func)


def _resolve_registry_points(cls, base, dct):
    module = cls.__module__
    parents = [x for x in cls.__mro__ if x not in (cls, SpecSet, object)]

    for k, v in dct.items():
        if isinstance(v, RegistryPoint):
            v.__name__ = k
            cls.registry[k] = v

        if is_datasource(v):
            v.__qualname__ = ".".join([cls.__name__, k])
            v.__name__ = k
            v.__module__ = module
            setattr(cls, k, SpecDescriptor(v))
            if k in base.registry:
                point = base.registry[k]
                dr.add_dependency(point, v)
                dr.mark_hidden(v)
                _register_context_handler(parents, v)


class SpecSetMeta(type):
    """
    The metaclass that converts RegistryPoint markers to regisry point
    datasources and hooks implementations for them into the registry.
    """
    def __new__(cls, name, bases, dct):
        dct["context_handlers"] = defaultdict(lambda: defaultdict(list))
        dct["registry"] = {}
        return super(SpecSetMeta, cls).__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        if name == "SpecSet":
            return
        if len(bases) > 1:
            raise Exception("SpecSet subclasses must inherit from only one class.")
        _resolve_registry_points(cls, bases[0], dct)


class SpecSet(six.with_metaclass(SpecSetMeta)):
    """
    The base class for all spec declarations. Extend this class and define your
    datasources directly or with a `SpecFactory`.
    """
    pass


def _get_context(context, broker):
    if isinstance(context, list):
        return dr.first_of(context, broker)
    return broker.get(context)


class simple_file(object):
    """
    Creates a datasource that reads the file at path when evaluated.

    Args:
        path (str): path to the file to read
        context (ExecutionContext): the context under which the datasource
            should run.
        kind (FileProvider): One of TextFileProvider or RawFileProvider.

    Returns:
        function: A datasource that reads all files matching the glob patterns.
    """
    def __init__(self, path, context=None, kind=TextFileProvider):
        self.path = path
        self.context = context or FSRoots
        self.kind = kind
        self.raw = kind is RawFileProvider
        self.__name__ = self.__class__.__name__
        datasource(self.context, raw=self.raw)(self)

    def __call__(self, broker):
        ctx = _get_context(self.context, broker)
        return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self)


class glob_file(object):
    """
    Creates a datasource that reads all files matching the glob pattern(s).

    Args:
        patterns (str or [str]): glob pattern(s) of paths to read.
        ignore (regex): a regular expression that is used to filter the paths
            matched by pattern(s).
        context (ExecutionContext): the context under which the datasource
            should run.
        kind (FileProvider): One of TextFileProvider or RawFileProvider.
        max_files (int): Maximum number of glob files to process.

    Returns:
        function: A datasource that reads all files matching the glob patterns.
    """
    def __init__(self, patterns, ignore=None, context=None, kind=TextFileProvider, max_files=1000):
        if not isinstance(patterns, (list, set)):
            patterns = [patterns]
        self.patterns = patterns
        self.ignore = ignore
        self.ignore_func = re.compile(ignore).search if ignore else lambda x: False
        self.context = context or FSRoots
        self.kind = kind
        self.raw = kind is RawFileProvider
        self.max_files = max_files
        self.__name__ = self.__class__.__name__
        datasource(self.context, multi_output=True, raw=self.raw)(self)

    def __call__(self, broker):
        ctx = _get_context(self.context, broker)
        root = ctx.root
        results = []
        for pattern in self.patterns:
            pattern = ctx.locate_path(pattern)
            for path in sorted(glob(os.path.join(root, pattern.lstrip('/')))):
                if self.ignore_func(path) or os.path.isdir(path):
                    continue
                try:
                    results.append(self.kind(path[len(root):], root=root, ds=self))
                except:
                    log.debug(traceback.format_exc())
        if results:
            if len(results) > self.max_files:
                raise ContentException("Number of files returned [{0}] is over the {1} file limit, please refine "
                                       "the specs file pattern to narrow down results".format(len(results), self.max_files))
            return results
        raise ContentException("[%s] didn't match." % ', '.join(self.patterns))


class head(object):
    """
    Return the first element of any datasource that produces a list.
    """
    def __init__(self, dep):
        self.dep = dep
        self.__name__ = self.__class__.__name__
        datasource(dep)(self)

    def __call__(self, lst):
        c = lst[self.dep]
        if lst:
            return c[0]
        raise dr.SkipComponent()


class first_file(object):
    """
    Creates a datasource that returns the first existing and readable file in
    files.

    Args:
        files (str): list of paths to find and read
        context (ExecutionContext): the context under which the datasource
            should run.
        kind (FileProvider): One of TextFileProvider or RawFileProvider.

    Returns:
        function: A datasource that returns the first file in files that exists
            and is readable
    """

    def __init__(self, files, context=None, kind=TextFileProvider):
        self.files = files
        self.context = context or FSRoots
        self.kind = kind
        self.raw = kind is RawFileProvider
        self.__name__ = self.__class__.__name__
        datasource(self.context, raw=self.raw)(self)

    def __call__(self, broker):
        ctx = _get_context(self.context, broker)
        root = ctx.root
        for f in self.files:
            try:
                return self.kind(ctx.locate_path(f), root=root, ds=self)
            except:
                pass
        raise ContentException("None of [%s] found." % ', '.join(self.files))


class listdir(object):
    """
    Execute a simple directory listing of all the files and directories in
    path.

    Args:
        path (str): directory or glob pattern to list.
        context (ExecutionContext): the context under which the datasource
            should run.
        ignore (str): regular expression defining paths to ignore.

    Returns:
        function: A datasource that returns the list of files and directories
            in the directory specified by path
    """

    def __init__(self, path, context=None, ignore=None):
        self.path = path
        self.context = context or FSRoots
        self.ignore = ignore
        self.ignore_func = re.compile(ignore).search if ignore else lambda x: False
        self.__name__ = self.__class__.__name__
        datasource(self.context)(self)

    def __call__(self, broker):
        ctx = _get_context(self.context, broker)
        p = os.path.join(ctx.root, self.path.lstrip('/'))
        p = ctx.locate_path(p)
        result = sorted(os.listdir(p)) if os.path.isdir(p) else sorted(glob(p))

        if result:
            return [os.path.basename(r) for r in result if not self.ignore_func(r)]
        raise ContentException("Can't list %s or nothing there." % p)


class simple_command(object):
    """
    Executable a simple command that has no dynamic arguments

    Args:
        cmd (list of lists): the command(s) to execute. Breaking apart a command
            string that might contain multiple commands separated by a pipe,
            getting them ready for subproc operations.
            IE. A command with filters applied
        context (ExecutionContext): the context under which the datasource
            should run.
        split (bool): whether the output of the command should be split into a
            list of lines
        keep_rc (bool): whether to return the error code returned by the
            process executing the command. If False, any return code other than
            zero with raise a CalledProcessError. If True, the return code and
            output are always returned.
        timeout (int): Number of seconds to wait for the command to complete.
            If the timeout is reached before the command returns, a
            CalledProcessError is raised. If None, timeout is infinite.

    Returns:
        function: A datasource that returns the output of a command that takes
            no arguments
    """

    def __init__(self, cmd, context=HostContext, split=True, keep_rc=False, timeout=None):
        self.cmd = cmd
        self.context = context
        self.split = split
        self.keep_rc = keep_rc
        self.timeout = timeout
        COMMANDS[self] = cmd
        self.__name__ = self.__class__.__name__
        datasource(self.context)(self)

    def __call__(self, broker):
        ctx = broker[self.context]
        rc = None
        if self.split:
            filters = "\n".join(get_filters(self))
        if filters:
            command = [shlex.split(self.cmd)] + [["grep", "-F", filters]]
            raw = ctx.shell_out(command, split=self.split, keep_rc=self.keep_rc, timeout=self.timeout)
        else:
            command = [shlex.split(self.cmd)]
            raw = ctx.shell_out(command, split=self.split, keep_rc=self.keep_rc, timeout=self.timeout)
        if self.keep_rc:
            rc, result = raw
        else:
            result = raw
        return CommandOutputProvider(self.cmd, ctx, split=self.split, content=result, rc=rc, keep_rc=self.keep_rc)


class foreach_execute(object):
    """
    Execute a command for each element in provider. Provider is the output of
    a different datasource that returns a list of single elements or a list of
    tuples. The command should have %s substitution parameters equal to the
    number of elements in each tuple of the provider.

    Args:
        provider (list): a list of elements or tuples.
        cmd (list of lists): a command with substitution parameters. Breaking
            apart a command string that might contain multiple commands
            separated by a pipe, getting them ready for subproc operations.
            IE. A command with filters applied
        context (ExecutionContext): the context under which the datasource
            should run.
        split (bool): whether the output of the command should be split into a
            list of lines
        keep_rc (bool): whether to return the error code returned by the
            process executing the command. If False, any return code other than
            zero with raise a CalledProcessError. If True, the return code and
            output are always returned.
        timeout (int): Number of seconds to wait for the command to complete.
            If the timeout is reached before the command returns, a
            CalledProcessError is raised. If None, timeout is infinite.

    Returns:
        function: A datasource that returns a list of outputs for each command
        created by substituting each element of provider into the cmd template.
    """

    def __init__(self, provider, cmd, context=HostContext, split=True, keep_rc=False, timeout=None):
        self.provider = provider
        self.cmd = cmd
        self.context = context
        self.split = split
        self.keep_rc = keep_rc
        self.timeout = timeout
        self.__name__ = self.__class__.__name__
        datasource(self.provider, self.context, multi_output=True)(self)

    def __call__(self, broker):
        result = []
        source = broker[self.provider]
        ctx = broker[self.context]
        if isinstance(source, ContentProvider):
            source = source.content
        if not isinstance(source, (list, set)):
            source = [source]
        for e in source:
            try:
                the_cmd = self.cmd % e
                rc = None

                if self.split:
                    filters = "\n".join(get_filters(self))
                if filters:
                    command = [shlex.split(the_cmd)] + [["grep", "-F", filters]]
                    raw = ctx.shell_out(command, split=self.split, keep_rc=self.keep_rc, timeout=self.timeout)
                else:
                    command = [shlex.split(the_cmd)]
                    raw = ctx.shell_out(command, split=self.split, keep_rc=self.keep_rc, timeout=self.timeout)
                if self.keep_rc:
                    rc, output = raw
                else:
                    output = raw
                result.append(CommandOutputProvider(the_cmd, ctx, args=e, content=output, rc=rc, split=self.split,
                                                    keep_rc=self.keep_rc))
            except:
                log.debug(traceback.format_exc())
        if result:
            return result
        raise ContentException("No results found for [%s]" % self.cmd)


class foreach_collect(object):
    """
    Subtitutes each element in provider into path and collects the files at the
    resulting paths.

    Args:
        provider (list): a list of elements or tuples.
        path (str): a path template with substitution parameters.
        context (ExecutionContext): the context under which the datasource
            should run.
        kind (FileProvider): one of TextFileProvider or RawFileProvider

    Returns:
        function: A datasource that returns a list of file contents created by
            substituting each element of provider into the path template.
    """

    def __init__(self, provider, path, ignore=None, context=HostContext, kind=TextFileProvider):
        self.provider = provider
        self.path = path
        self.ignore = ignore
        self.ignore_func = re.compile(ignore).search if ignore else lambda x: False
        self.context = context
        self.kind = kind
        self.raw = kind is RawFileProvider
        self.__name__ = self.__class__.__name__
        datasource(self.provider, self.context, multi_output=True, raw=self.raw)(self)

    def __call__(self, broker):
        result = []
        source = broker[self.provider]
        ctx = _get_context(self.context, broker)
        root = ctx.root
        if isinstance(source, ContentProvider):
            source = source.content
        if not isinstance(source, (list, set)):
            source = [source]
        for e in source:
            pattern = ctx.locate_path(self.path % e)
            for p in glob(os.path.join(root, pattern.lstrip('/'))):
                if self.ignore_func(p) or os.path.isdir(p):
                    continue
                try:
                    result.append(self.kind(p[len(root):], root=root, ds=self))
                except:
                    log.debug(traceback.format_exc())
        if result:
            return result
        raise ContentException("No results found for [%s]" % self.path)


class first_of(object):
    """ Given a list of dependencies, returns the first of the list
        that exists in the broker. At least one must be present, or this
        component won't fire.
    """
    def __init__(self, deps):
        self.deps = deps
        dr.mark_hidden(deps)
        self.__name__ = self.__class__.__name__
        datasource(deps)(self)

    def __call__(self, broker):
        for c in self.deps:
            if c in broker:
                return broker[c]


@serializer(TextFileProvider)
def serialize_text_provider(obj):
    d = {}
    d["path"] = obj.path
    d["_content"] = obj.content
    return d


@serializer(CommandOutputProvider)
def serialize_command_provider(obj):
    d = {}
    d["rc"] = obj.rc
    d["cmd"] = obj.cmd
    d["args"] = obj.args
    d["path"] = obj.path
    d["_content"] = obj.content
    return d


@deserializer(ContentProvider)
def deserialize_content(_type, obj):
    c = ContentProvider()
    for k, v in obj.items():
        setattr(c, k, v)
    return c
