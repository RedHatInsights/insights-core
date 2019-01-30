import logging
import os

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


def determine_context(common_path, files):
    if any(f.endswith(archives.COMPRESSION_TYPES) for f in os.listdir(common_path)):
        return ClusterArchiveContext

    for f in files:
        if "insights_archive.txt" in f:
            return SerializedArchiveContext
        elif "insights_commands" in f:
            return HostArchiveContext
        elif "sos_commands" in f:
            return SosArchiveContext
        elif "JBOSS_HOME" in f:
            return JDRContext

    return HostArchiveContext


def create_context(path, context=None):
    all_files = get_all_files(path)
    if not all_files:
        raise archives.InvalidArchive("No files in archive")

    common_path = os.path.dirname(os.path.commonprefix(all_files))
    if not common_path:
        raise archives.InvalidArchive("Unable to determine common path")

    context = context or determine_context(common_path, all_files)
    return context(common_path, all_files=all_files)
