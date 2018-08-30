import logging
import os

from insights.core import archives
from insights.core.archives import COMPRESSION_TYPES
from insights.core.context import ClusterArchiveContext, JDRContext, HostArchiveContext, SosArchiveContext

log = logging.getLogger(__name__)


def get_all_files(path):
    all_files = []
    for f in archives.get_all_files(path):
        if os.path.isfile(f) and not os.path.islink(f):
            all_files.append(f)
    return all_files


def determine_context(common_path, files):
    if any(f.endswith(COMPRESSION_TYPES) for f in os.listdir(common_path)):
        return ClusterArchiveContext

    for f in files:
        if "insights_commands" in f:
            return HostArchiveContext
        elif "sos_commands" in f:
            return SosArchiveContext
        elif "JBOSS_HOME" in f:
            return JDRContext

    return HostArchiveContext


def create_context(path, context=None):
    all_files = get_all_files(path)
    common_path = os.path.dirname(os.path.commonprefix(all_files))
    context = context or determine_context(common_path, all_files)
    return context(common_path, all_files=all_files)
