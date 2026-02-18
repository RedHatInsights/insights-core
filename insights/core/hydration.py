import logging
import os

from insights.core import archives, dr
from insights.core.context import (
    ClusterArchiveContext,
    ExecutionContextMeta,
    HostArchiveContext,
    SerializedArchiveContext,
)
from insights.core.exceptions import ContextException, InvalidArchive
from insights.core.serde import Hydration

log = logging.getLogger(__name__)

if hasattr(os, "scandir"):

    def get_all_files(path):
        with os.scandir(path) as it:
            for ent in it:
                try:
                    if ent.is_dir(follow_symlinks=False):
                        for pth in get_all_files(ent.path):
                            yield pth
                    elif ent.is_file(follow_symlinks=False):
                        yield ent.path
                except OSError as ex:
                    log.exception(ex)

else:

    def get_all_files(path):
        for root, _, files in os.walk(path):
            for f in files:
                full_path = os.path.join(root, f)
                if os.path.isfile(full_path) and not os.path.islink(full_path):
                    yield full_path


def identify(files):
    common_path, ctx = ExecutionContextMeta.identify(files)
    if ctx:
        return common_path, ctx

    common_path = os.path.dirname(os.path.commonprefix(files))
    if not common_path:
        raise InvalidArchive("Unable to determine common path")

    return common_path, HostArchiveContext


def _create_cluster_archive_context(path):
    top = os.listdir(path)
    arc = [
        os.path.join(path, f)
        for f in top
        if f.endswith(archives.COMPRESSION_TYPES) and os.path.isfile(os.path.join(path, f))
    ]

    return ClusterArchiveContext(path, all_files=arc) if arc else None


def create_context(path, context=None):
    all_files = list(get_all_files(path))
    if not all_files:
        raise InvalidArchive("No files in archive")

    # try given context
    # this block is unable to select ClusterArchiveContext
    if context:
        common_path, ctx = context.handles(all_files)
        if ctx is not None:
            return ctx(common_path, all_files=all_files)

    # try ClusterArchiveContext
    cac_ctx = _create_cluster_archive_context(path)
    # do not use ClusterArchiveContext if the user specified another execution context
    if cac_ctx and (context is None or context == ClusterArchiveContext):
        return cac_ctx
    # remember that we found ClusterArchiveContext if a user-defined context was not found
    elif cac_ctx and context is not None:
        ctx = ClusterArchiveContext
    # use standard auto-detection (falls back to HostArchiveContext if nothing else is detected)
    else:
        common_path, ctx = identify(all_files)

    # The specified context was not found and it is not HostArchiveContext; suggest the
    # auto-detected one.
    # `context` and `ctx` will be identical at this point only if both are HostArchiveContext. This
    # will occur when no execution context is found in the path and identify() falls back to
    # HostArchiveContext. To maintain consistent behavior between user-defined context and
    # auto-detected one, we need to allow its creation even though the marker was not found.
    if context is not None and context is not ctx:
        raise ContextException(
            "Cannot find execution context '{0}.{1}' in path: {2}\n  Did you mean '{3}.{4}'?".format(
                context.__module__,
                context.__name__,
                path,
                ctx.__module__,
                ctx.__name__,
            )
        )

    # we get here only if no specific execution context was requested
    return ctx(common_path, all_files=all_files)


def initialize_broker(path, context=None, broker=None):
    ctx = create_context(path, context=context)
    broker = broker or dr.Broker()
    if isinstance(ctx, ClusterArchiveContext):
        return ctx, broker

    broker[ctx.__class__] = ctx
    if isinstance(ctx, SerializedArchiveContext):
        h = Hydration(root=ctx.root, ctx=ctx)
        broker = h.hydrate(broker=broker)
    return ctx, broker
