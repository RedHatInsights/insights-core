import logging
import os
import re
import six
import sys
import traceback

from collections import defaultdict
from glob import glob

from insights.core import dr
from insights.core.context import FileArchiveContext, FSRoots, HostContext
from insights.core.plugins import datasource, ContentException
from insights.core.serde import deserializer, serializer

log = logging.getLogger(__name__)

FILTERS = defaultdict(set)


def add_filter(name, patterns):
    if isinstance(patterns, six.string_types):
        FILTERS[name].add(patterns)
    elif isinstance(patterns, list):
        FILTERS[name] |= set(patterns)
    elif isinstance(patterns, set):
        FILTERS[name] |= patterns
    else:
        raise TypeError("patterns must be string, list, or set.")


def get_filters(component):
    filters = set()
    if component in FILTERS:
        filters |= FILTERS[component]

    alias = dr.get_alias_for(component)
    if alias and alias in FILTERS:
        filters |= FILTERS[alias]
    return filters


def mangle_command(command, name_max=255):
    pattern = r"[^\w\-\.\/\?]+"

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
        self._content = None
        self._exception = None

    @property
    def content(self):
        if self._exception:
            raise self._exception

        if not self._content:
            try:
                self._content = self.load()
            except Exception as ex:
                self._exception = ex
                raise

        return self._content

    def __unicode__(self):
        return self.content

    def __str__(self):
        return self.__unicode__()


class FileProvider(ContentProvider):
    def __init__(self, root, relative_path, filters=None):
        super(FileProvider, self).__init__()
        self.relative_path = relative_path.lstrip("/")
        self.root = root

        self.path = os.path.join(root, self.relative_path)
        self.file_name = os.path.basename(self.path)

        self.filters = filters or set()
        self.validate()

    def validate(self):
        if not os.path.exists(self.path):
            raise ContentException("%s does not exist." % self.path)

        if not os.access(self.path, os.R_OK):
            raise ContentException("Cannot access %s" % self.path)

    def __repr__(self):
        return '%s("%s") - %s' % (self.__class__.__name__, self.path, self.root)


class RawFileProvider(FileProvider):
    def load(self):
        with open(self.path, 'rb') as f:
            return f.read()


class TextFileProvider(FileProvider):
    def load(self):
        with open(self.path, 'r') as f:
            if self.filters:
                # This should shell out to a grep pipeline
                return [l.rstrip() for l in f.readlines() if any(s in l for s in self.filters)]
            else:
                return [l.rstrip() for l in f.readlines()]


class CommandOutputProvider(ContentProvider):
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

    def load(self):
        if self.keep_rc:
            self.rc, result = self.ctx.shell_out(self.cmd, self.split, keep_rc=True)
            return result
        else:
            return self.ctx.shell_out(self.cmd, self.split)

    def __repr__(self):
        return 'CommandOutputProvider("%s")' % self.cmd


class SpecFactory(object):
    def __init__(self, module_name="insights.specs"):
        self.module_name = module_name

    def attach(self, component, name):
        """ Attach component to a module by name. """

        module = sys.modules[self.module_name]
        old = getattr(module, name, None)
        component.__module__ = self.module_name
        component.__name__ = name
        setattr(module, name, component)
        if old:
            dr.replace(old, component)

    def simple_file(self, path, name=None, context=None, Kind=TextFileProvider, alias=None):
        @datasource(requires=[context or FSRoots], alias=alias)
        def inner(broker):
            root = (broker.get(context) or dr.first_of(FSRoots, broker)).root
            return Kind(root, os.path.expandvars(path), filters=get_filters(inner))
        if name:
            self.attach(inner, name)
        return inner

    def glob_file(self, patterns, name=None, ignore=None, context=None, Kind=TextFileProvider, alias=None):
        if not isinstance(patterns, (list, set)):
            patterns = [patterns]

        @datasource(requires=[context or FSRoots], alias=alias)
        def inner(broker):
            root = (broker.get(context) or dr.first_of(FSRoots, broker)).root
            results = []
            for pattern in patterns:
                pattern = os.path.expandvars(pattern)
                for path in glob(os.path.join(root, pattern.lstrip('/'))):
                    if ignore and re.search(ignore, path):
                        continue
                    try:
                        results.append(Kind(root, path[len(root):], filters=get_filters(inner)))
                    except:
                        log.debug(traceback.format_exc())
            if results:
                return results
            raise ContentException("[%s] didn't match" % ','.join(patterns))
        if name:
            self.attach(inner, name)
        return inner

    def first_file(self, files, name=None, context=None, Kind=TextFileProvider, alias=None):
        @datasource(requires=[context or FSRoots], alias=alias)
        def inner(broker):
            root = (broker.get(context) or dr.first_of(FSRoots, broker)).root
            for f in files:
                try:
                    return Kind(root, f, filters=get_filters(inner))
                except:
                    pass
            raise ContentException("None of [%s] found." % ','.join(files))
        if name:
            self.attach(inner, name)
        return inner

    def listdir(self, path, name=None, context=None, alias=None):
        @datasource(requires=[context or FSRoots], alias=alias)
        def inner(broker):
            root = (broker.get(context) or dr.first_of(FSRoots, broker)).root
            p = os.path.join(root, path.lstrip('/'))
            if os.path.isdir(p):
                return os.listdir(p)

            result = glob(p)
            if result:
                return [os.path.basename(r) for r in result]
            raise ContentException("Can't list %s or nothing there." % p)
        if name:
            self.attach(inner, name)
        return inner

    def simple_command(self, cmd, name=None, context=HostContext, split=True, keep_rc=False, alias=None):
        @datasource(requires=[context], alias=alias)
        def inner(broker):
            ctx = broker[context]
            rc = None
            raw = ctx.shell_out(cmd, split=split, keep_rc=keep_rc)
            if keep_rc:
                rc, result = raw
            else:
                result = raw
            return CommandOutputProvider(cmd, ctx, split=split, content=result, rc=rc, keep_rc=keep_rc)
        if name:
            self.attach(inner, name)
        return inner

    def with_args_from(self, provider, cmd, name=None, context=HostContext, split=True, keep_rc=False, alias=None):
        @datasource(requires=[provider, context], alias=alias)
        def inner(broker):
            result = []
            source = broker[provider]
            ctx = broker[context]
            if isinstance(source, ContentProvider):
                source = source.content
            if not isinstance(source, (list, set)):
                source = [source]
            for e in source:
                try:
                    the_cmd = cmd % e
                    rc = None
                    raw = ctx.shell_out(the_cmd, split=split, keep_rc=keep_rc)
                    if keep_rc:
                        rc, output = raw
                    else:
                        output = raw
                    result.append(CommandOutputProvider(the_cmd, ctx, args=e, content=output, rc=rc, split=split, keep_rc=keep_rc))
                except:
                    log.debug(traceback.format_exc())
            if result:
                return result
            raise ContentException("No results found for [%s]" % cmd)
        if name:
            self.attach(inner, name)
        return inner

    def stored_command(self,
                       pattern,
                       name=None,
                       context=FileArchiveContext,
                       Kind=TextFileProvider,
                       replace_regex="([a-zA-Z0-9]+)",
                       alias=None):
        has_group = "?" in pattern
        pattern = mangle_command(pattern).replace("?", replace_regex) + "$"

        @datasource(requires=[context], alias=alias)
        def inner(broker):
            ctx = broker[context]
            root = ctx.root
            results = []
            pat = os.path.join(ctx.stored_command_prefix, pattern)
            for path in broker[context].file_paths:
                m = re.match(pat, path)
                if m:
                    results.append(Kind(root, path, filters=get_filters(inner)))
            if not results:
                raise ContentException("[%s] didn't match." % pat)

            if not has_group and len(results) == 1:
                return results[0]
            return results

        if name:
            self.attach(inner, name)
        return inner

    def first_of(self, deps, name=None, alias=None):
        """ Given a list of dependencies, returns the first of the list
            that exists in the broker. At least one must be present, or this
            component won't fire.
        """
        dr.mark_hidden(deps)

        @datasource(requires=[deps], alias=alias)
        def inner(broker):
            for c in deps:
                if c in broker:
                    return broker[c]

        if name:
            self.attach(inner, name)
        return inner


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
