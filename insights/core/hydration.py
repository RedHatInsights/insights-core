import logging
import os

from insights.core import archives, dr
from insights.core.context import (ClusterArchiveContext, ExecutionContextMeta, HostArchiveContext,
                                   SerializedArchiveContext)
from insights.core.exceptions import InvalidArchive
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


def create_context(path, context=None):
    top = os.listdir(path)
    arc = [os.path.join(path, f) for f in top
           if f.endswith(archives.COMPRESSION_TYPES) and
           os.path.isfile(os.path.join(path, f))]
    if arc:
        return ClusterArchiveContext(path, all_files=arc)

    all_files = list(get_all_files(path))
    if not all_files:
        raise InvalidArchive("No files in archive")

    common_path, ctx = identify(all_files)
    context = context or ctx
    return context(common_path, all_files=all_files)


def initialize_broker(path, context=None, broker=None):
    ctx = create_context(path, context=context)
    broker = broker or dr.Broker()
    if isinstance(ctx, ClusterArchiveContext):
        return ctx, broker

    broker[ctx.__class__] = ctx
    if isinstance(ctx, SerializedArchiveContext):
        h = Hydration(ctx.root)
        broker = h.hydrate(broker=broker)
    return ctx, broker
