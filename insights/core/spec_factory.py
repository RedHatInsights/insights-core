import itertools
import logging
import os
import re
import six
import traceback

from collections import defaultdict
from glob import glob
from subprocess import call

from insights.core import blacklist, dr
from insights.core.filters import get_filters
from insights.core.context import ExecutionContext, FSRoots, HostContext
from insights.core.plugins import datasource, ContentException, is_datasource
from insights.util import fs, streams, which
from insights.util.subproc import Pipeline
from insights.core.serde import deserializer, serializer
import shlex

log = logging.getLogger(__name__)


SAFE_ENV = {
    "PATH": os.path.pathsep.join([
        "/bin",
        "/usr/bin",
        "/sbin",
        "/usr/sbin",
        "/usr/share/Modules/bin",
    ]),
    "LC_ALL": "C",
}
"""
A minimal set of environment variables for use in subprocess calls
"""
if "LANG" in os.environ:
    SAFE_ENV["LANG"] = os.environ["LANG"]


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
        self.root = None
        self.relative_path = None
        self.loaded = False
        self._content = None
        self._exception = None

    def load(self):
        raise NotImplemented()

    def stream(self):
        """
        Returns a generator of lines instead of a list of lines.
        """
        st = self._stream()
        for l in next(st):
            yield l.rstrip("\n")

    def _stream(self):
        raise NotImplementedError()

    @property
    def path(self):
        return os.path.join(self.root, self.relative_path)

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
        msg = "<%s(path=%r, cmd=%r)>"
        return msg % (self.__class__.__name__, self.path or "", self.cmd or "")

    def __unicode__(self):
        return self.__repr__()

    def __str__(self):
        return self.__unicode__()


class DatasourceProvider(ContentProvider):
    def __init__(self, content, relative_path, root='/', ds=None, ctx=None):
        super(DatasourceProvider, self).__init__()
        self.relative_path = relative_path
        self._content = content if isinstance(content, list) else content.splitlines()
        self.root = root
        self.ds = ds
        self.ctx = ctx

    def _stream(self):
        """
        Returns a generator of lines instead of a list of lines.
        """
        yield self._content

    def write(self, dst):
        fs.ensure_path(os.path.dirname(dst))
        with open(dst, "wb") as f:
            f.write("\n".join(self.content).encode("utf-8"))

        self.loaded = False
        self._content = None

    def load(self):
        return self.content


class FileProvider(ContentProvider):
    def __init__(self, relative_path, root="/", ds=None, ctx=None):
        super(FileProvider, self).__init__()
        self.root = root
        self.relative_path = relative_path.lstrip("/")
        self.file_name = os.path.basename(self.path)

        self.ds = ds
        self.ctx = ctx
        self.validate()

    def validate(self):
        if not blacklist.allow_file("/" + self.relative_path):
            raise dr.SkipComponent()

        if not os.path.exists(self.path):
            raise ContentException("%s does not exist." % self.path)

        resolved = os.path.realpath(self.path)
        if not resolved.startswith(os.path.realpath(self.root)):
            msg = "Relative path points outside the root: %s -> %s."
            raise Exception(msg % (self.path, resolved))

        if not os.access(self.path, os.R_OK):
            raise ContentException("Cannot access %s" % self.path)

    def __repr__(self):
        return '%s("%r")' % (self.__class__.__name__, self.path)


class RawFileProvider(FileProvider):
    """
    Class used in datasources that returns the contents of a file a single
    string. The file is not filtered.
    """

    def load(self):
        self.loaded = True
        with open(self.path, 'rb') as f:
            return f.read()

    def write(self, dst):
        fs.ensure_path(os.path.dirname(dst))
        call([which("cp", env=SAFE_ENV), self.path, dst], env=SAFE_ENV)


class TextFileProvider(FileProvider):
    """
    Class used in datasources that returns the contents of a file a list of
    lines. Each line is filtered if filters are defined for the datasource.
    """

    def create_args(self):
        args = []
        filters = "\n".join(get_filters(self.ds)) if self.ds else None
        if filters:
            args.append(["grep", "-F", filters, self.path])

        patterns = "\n".join(blacklist.get_disallowed_patterns())
        if patterns:
            grep = ["grep", "-v" "-F", patterns]
            if not args:
                grep.append(self.path)
            args.append(grep)

        keywords = blacklist.get_disallowed_keywords()
        if keywords:
            sed = ["sed"]
            for kw in keywords:
                sed.extend(["-e", "s/%s/keyword/g" % kw.replace("/", "\\/")])
            if not args:
                sed.append(self.path)
            args.append(sed)
        return args

    def load(self):
        self.loaded = True
        args = self.create_args()
        if args:
            rc, out = self.ctx.shell_out(args, keep_rc=True, env=SAFE_ENV)
            self.rc = rc
            return out
        with open(self.path, "rU") as f:  # universal newlines
            return [l.rstrip("\n") for l in f]

    def _stream(self):
        """
        Returns a generator of lines instead of a list of lines.
        """
        if self._exception:
            raise self._exception
        try:
            if self._content:
                yield self._content
            else:
                args = self.create_args()
                if args:
                    with streams.connect(*args, env=SAFE_ENV) as s:
                        yield s
                else:
                    with open(self.path, "rU") as f:  # universal newlines
                        yield f
        except StopIteration:
            raise
        except Exception as ex:
            self._exception = ex
            raise ContentException(str(ex))

    def write(self, dst):
        fs.ensure_path(os.path.dirname(dst))
        args = self.create_args()
        if args:
            p = Pipeline(*args, env=SAFE_ENV)
            p.write(dst)
        else:
            call([which("cp", env=SAFE_ENV), self.path, dst], env=SAFE_ENV)


class SerializedOutputProvider(TextFileProvider):
    def create_args(self):
        pass


class SerializedRawOutputProvider(RawFileProvider):
    pass


class CommandOutputProvider(ContentProvider):
    """
    Class used in datasources to return output from commands.
    """
    def __init__(self, cmd, ctx, args=None, split=True, keep_rc=False, ds=None, timeout=None, inherit_env=None):
        super(CommandOutputProvider, self).__init__()
        self.cmd = cmd
        self.root = "insights_commands"
        self.relative_path = os.path.join("insights_commands", mangle_command(cmd))
        self.ctx = ctx
        self.args = args  # already interpolated into cmd - stored here for context.
        self.split = split
        self.keep_rc = keep_rc
        self.ds = ds
        self.timeout = timeout
        self.inherit_env = inherit_env or []

        self._content = None
        self.rc = None

        self.validate()

    def validate(self):
        if not blacklist.allow_command(self.cmd):
            raise dr.SkipComponent()

        if not which(shlex.split(self.cmd)[0], env=self.create_env()):
            raise ContentException("Couldn't execute: %s" % self.cmd)

    def create_args(self):
        command = [shlex.split(self.cmd)]

        if self.split:
            filters = "\n".join(get_filters(self.ds))
            if filters:
                command.append(["grep", "-F", filters])

            patterns = "\n".join(blacklist.get_disallowed_patterns())
            if patterns:
                command.append(["grep", "-v", "-F", patterns])

            keywords = blacklist.get_disallowed_keywords()
            if keywords:
                sed = ["sed"]
                for kw in keywords:
                    sed.extend(["-e", "s/%s/keyword/g" % kw.replace("/", "\\/")])
                command.append(sed)
        return command

    def create_env(self):
        env = dict(SAFE_ENV)
        for e in self.inherit_env:
            if e in os.environ:
                env[e] = os.environ[e]
        return env

    def load(self):
        command = self.create_args()

        raw = self.ctx.shell_out(command, split=self.split, keep_rc=self.keep_rc,
                timeout=self.timeout, env=self.create_env())
        if self.keep_rc:
            self.rc, output = raw
        else:
            output = raw
        return output

    def _stream(self):
        """
        Returns a generator of lines instead of a list of lines.
        """
        if self._exception:
            raise self._exception
        try:
            if self._content:
                yield self._content
            else:
                args = self.create_args()
                with self.ctx.connect(*args, env=self.create_env(), timeout=self.timeout) as s:
                    yield s
        except StopIteration:
            raise
        except Exception as ex:
            self._exception = ex
            raise ContentException(str(ex))

    def write(self, dst):
        args = self.create_args()
        fs.ensure_path(os.path.dirname(dst))
        if args:
            p = Pipeline(*args, timeout=self.timeout, env=self.create_env())
            return p.write(dst, keep_rc=self.keep_rc)

    def __repr__(self):
        return 'CommandOutputProvider("%r")' % self.cmd


class RegistryPoint(object):
    # Marker class for declaring that an element of a `SpecSet` subclass
    # is a registry point against which further subclasses can register
    # datasource implementations by simply declaring them with the same name.
    #
    # intentionally not a docstring so this doesn't show up in pydoc.
    def __init__(self, metadata=None, multi_output=False, raw=False,
            filterable=False):
        self.metadata = metadata
        self.multi_output = multi_output
        self.raw = raw
        self.filterable = filterable
        self.__name__ = self.__class__.__name__
        datasource([], metadata=metadata, multi_output=multi_output, raw=raw,
                filterable=filterable)(self)

    def __call__(self, broker):
        for c in reversed(dr.get_delegate(self).deps):
            if c in broker:
                return broker[c]
        raise dr.SkipComponent()

    def __repr__(self):
        return dr.get_name(self)


class SpecDescriptor(object):
    # Descriptor Protocol handler that returns the literal function from a
    # class during dot (.) access.
    #
    # intentionally not a docstring so this doesn't show up in pydoc.
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        return self.func

    def __set__(self, obj, val):
        raise AttributeError()


def _get_ctx_dependencies(component):
    ctxs = set()
    for c in dr.walk_tree(component):
        try:
            if issubclass(c, ExecutionContext):
                ctxs.add(c)
        except:
            pass
    return ctxs


def _register_context_handler(parents, component):
    name = component.__name__
    parents = list(itertools.takewhile(lambda x: name in x.registry, parents))
    if not parents:
        return

    # If the new component handles a context, we need to tell the
    # previously registered components that would have handled it to ignore it.

    # The components that handle a context are registered on the highest class
    # of the MRO list. This is so overrides work correctly even if a
    # component isn't a direct sibling of the component it's overriding.

    # instead of trying to unhook all of the dependencies, we just tell the
    # previous handler of a context to ignore it.
    ctx_handlers = parents[-1].context_handlers
    for c in _get_ctx_dependencies(component):
        for old in ctx_handlers[name][c]:
            dr.add_ignore(old, c)
        ctx_handlers[name][c].append(component)


def _resolve_registry_points(cls, base, dct):
    module = cls.__module__
    parents = [x for x in cls.__mro__ if x not in (cls, SpecSet, object)]

    for k, v in dct.items():
        if isinstance(v, RegistryPoint):
            # add v under its name to this class's registry.
            v.__name__ = k
            cls.registry[k] = v

        if is_datasource(v):
            v.__qualname__ = ".".join([cls.__name__, k])
            v.__name__ = k
            v.__module__ = module
            setattr(cls, k, SpecDescriptor(v))
            if k in base.registry:
                # if the datasource has the same name as a RegistryPoint in the
                # base class, the datasource to the RegistryPoint.
                point = base.registry[k]

                # TODO: log when RegistryPoint and implementation properties
                # TODO: aren't the same.
                delegate = dr.get_delegate(v)
                v.filterable = delegate.filterable = point.filterable
                v.raw = delegate.raw = point.raw
                v.multi_output = delegate.multi_output = point.multi_output

                # the RegistryPoint gets the implementation datasource as a
                # dependency
                dr.add_dependency(point, v)

                # Datasources override previously defined datasources of the
                # same name for contexts they all depend on. Here we tell
                # datasources of the same name not to execute under contexts
                # the new datasource will handle.
                _register_context_handler(parents, v)


class SpecSetMeta(type):
    """
    The metaclass that converts RegistryPoint markers to registry point
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
    def __init__(self, path, context=None, deps=[], kind=TextFileProvider, **kwargs):
        self.path = path
        self.context = context or FSRoots
        self.kind = kind
        self.raw = kind is RawFileProvider
        self.__name__ = self.__class__.__name__
        datasource(self.context, *deps, raw=self.raw, **kwargs)(self)

    def __call__(self, broker):
        ctx = _get_context(self.context, broker)
        return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)


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
    def __init__(self, patterns, ignore=None, context=None, deps=[], kind=TextFileProvider, max_files=1000, **kwargs):
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
        datasource(self.context, *deps, multi_output=True, raw=self.raw, **kwargs)(self)

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
                    results.append(self.kind(path[len(root):], root=root, ds=self, ctx=ctx))
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
    def __init__(self, dep, **kwargs):
        self.dep = dep
        self.__name__ = self.__class__.__name__
        datasource(dep, **kwargs)(self)

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

    def __init__(self, paths, context=None, deps=[], kind=TextFileProvider, **kwargs):
        self.paths = paths
        self.context = context or FSRoots
        self.kind = kind
        self.raw = kind is RawFileProvider
        self.__name__ = self.__class__.__name__
        datasource(self.context, *deps, raw=self.raw, **kwargs)(self)

    def __call__(self, broker):
        ctx = _get_context(self.context, broker)
        root = ctx.root
        for p in self.paths:
            try:
                return self.kind(ctx.locate_path(p), root=root, ds=self, ctx=ctx)
            except:
                pass
        raise ContentException("None of [%s] found." % ', '.join(self.paths))


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

    def __init__(self, path, context=None, ignore=None, deps=[]):
        self.path = path
        self.context = context or FSRoots
        self.ignore = ignore
        self.ignore_func = re.compile(ignore).search if ignore else lambda x: False
        self.__name__ = self.__class__.__name__
        datasource(self.context, *deps)(self)

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
        inherit_env (list): The list of environment variables to inherit from the
            calling process when the command is invoked.

    Returns:
        function: A datasource that returns the output of a command that takes
            no arguments
    """

    def __init__(self, cmd, context=HostContext, deps=[], split=True, keep_rc=False, timeout=None, inherit_env=[], **kwargs):
        self.cmd = cmd
        self.context = context
        self.split = split
        self.raw = not split
        self.keep_rc = keep_rc
        self.timeout = timeout
        self.inherit_env = inherit_env
        self.__name__ = self.__class__.__name__
        datasource(self.context, *deps, raw=self.raw, **kwargs)(self)

    def __call__(self, broker):
        ctx = broker[self.context]
        return CommandOutputProvider(self.cmd, ctx, split=self.split,
                keep_rc=self.keep_rc, ds=self, timeout=self.timeout, inherit_env=self.inherit_env)


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
        inherit_env (list): The list of environment variables to inherit from the
            calling process when the command is invoked.


    Returns:
        function: A datasource that returns a list of outputs for each command
        created by substituting each element of provider into the cmd template.
    """

    def __init__(self, provider, cmd, context=HostContext, deps=[], split=True, keep_rc=False, timeout=None, inherit_env=[], **kwargs):
        self.provider = provider
        self.cmd = cmd
        self.context = context
        self.split = split
        self.raw = not split
        self.keep_rc = keep_rc
        self.timeout = timeout
        self.inherit_env = inherit_env
        self.__name__ = self.__class__.__name__
        datasource(self.provider, self.context, *deps, multi_output=True, raw=self.raw, **kwargs)(self)

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
                cop = CommandOutputProvider(the_cmd, ctx, args=e,
                        split=self.split, keep_rc=self.keep_rc, ds=self,
                        timeout=self.timeout, inherit_env=self.inherit_env)
                result.append(cop)
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

    def __init__(self, provider, path, ignore=None, context=HostContext, deps=[], kind=TextFileProvider, **kwargs):
        self.provider = provider
        self.path = path
        self.ignore = ignore
        self.ignore_func = re.compile(ignore).search if ignore else lambda x: False
        self.context = context
        self.kind = kind
        self.raw = kind is RawFileProvider
        self.__name__ = self.__class__.__name__
        datasource(self.provider, self.context, *deps, multi_output=True, raw=self.raw, **kwargs)(self)

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
                    result.append(self.kind(p[len(root):], root=root, ds=self, ctx=ctx))
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
        self.raw = deps[0].raw
        self.__name__ = self.__class__.__name__
        datasource(deps)(self)

    def __call__(self, broker):
        for c in self.deps:
            if c in broker:
                return broker[c]


@serializer(CommandOutputProvider)
def serialize_command_output(obj, root):
    rel = os.path.join("insights_commands", mangle_command(obj.cmd))
    dst = os.path.join(root, rel)
    rc = obj.write(dst)
    return {
        "rc": rc,
        "cmd": obj.cmd,
        "args": obj.args,
        "relative_path": rel
    }


@deserializer(CommandOutputProvider)
def deserialize_command_output(_type, data, root):
    rel = data["relative_path"]

    res = SerializedOutputProvider(rel, root)

    res.rc = data["rc"]
    res.cmd = data["cmd"]
    res.args = data["args"]
    return res


@serializer(TextFileProvider)
def serialize_text_file_provider(obj, root):
    dst = os.path.join(root, obj.relative_path)
    rc = obj.write(dst)
    return {
        "relative_path": obj.relative_path,
        "rc": rc,
    }


@deserializer(TextFileProvider)
def deserialize_text_provider(_type, data, root):
    rel = data["relative_path"]
    res = SerializedOutputProvider(rel, root)
    res.rc = data["rc"]
    return res


@serializer(RawFileProvider)
def serialize_raw_file_provider(obj, root):
    dst = os.path.join(root, obj.relative_path)
    rc = obj.write(dst)
    return {
        "relative_path": obj.relative_path,
        "rc": rc,
    }


@deserializer(RawFileProvider)
def deserialize_raw_file_provider(_type, data, root):
    rel = data["relative_path"]
    res = SerializedRawOutputProvider(rel, root)
    res.rc = data["rc"]
    return res


@serializer(DatasourceProvider)
def serialize_datasource_provider(obj, root):
    dst = os.path.join(root, obj.relative_path.lstrip("/"))
    fs.ensure_path(os.path.dirname(dst))
    obj.write(dst)
    return {"relative_path": obj.relative_path}


@deserializer(DatasourceProvider)
def deserialize_datasource_provider(_type, data, root):
    return SerializedRawOutputProvider(data["relative_path"], root)
