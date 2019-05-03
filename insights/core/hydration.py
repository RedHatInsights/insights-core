import logging
import os
from itertools import product

from insights.core import archives
from insights.core.context import (ClusterArchiveContext,
                                   JDRContext,
                                   HostArchiveContext,
                                   SosArchiveContext,
                                   SerializedArchiveContext)

log = logging.getLogger(__name__)


def get_all_files(path):
    all_files = []
    for f in archives.get_all_files(path):
        if os.path.isfile(f) and not os.path.islink(f):
            all_files.append(f)
    return all_files


def identify(files):
    markers = {"insights_archive.txt": SerializedArchiveContext,
               "insights_commands": HostArchiveContext,
               "sos_commands": SosArchiveContext,
               "JBOSS_HOME": JDRContext}

    for f, m in product(files, markers):
        if m in f:
            i = f.find(m)
            common_path = os.path.dirname(f[:i])
            ctx = markers[m]
            return common_path, ctx

    common_path = os.path.dirname(os.path.commonprefix(files))
    if not common_path:
        raise archives.InvalidArchive("Unable to determine common path")

    return common_path, HostArchiveContext


def create_context(path, context=None):
    top = os.listdir(path)
    arc = [os.path.join(path, f) for f in top if f.endswith(archives.COMPRESSION_TYPES)]
    if arc:
        return ClusterArchiveContext(path, all_files=arc)

    all_files = get_all_files(path)
    if not all_files:
        raise archives.InvalidArchive("No files in archive")

    common_path, ctx = identify(all_files)
    context = context or ctx
    return context(common_path, all_files=all_files)
