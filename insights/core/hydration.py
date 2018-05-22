import logging
import os

from insights.core import archives
from insights.core import dr
from insights.core import serde
from insights.core.archives import COMPRESSION_TYPES
from insights.core.context import ClusterArchiveContext, JDRContext, HostArchiveContext, SosArchiveContext
from insights.core.evaluators import SingleEvaluator

log = logging.getLogger(__name__)


def create_context(path, context=None):
    if context is None and any(f.endswith(COMPRESSION_TYPES) for f in os.listdir(path)):
        context = ClusterArchiveContext

    all_files = []
    for f in archives.get_all_files(path):
        if os.path.isfile(f) and not os.path.islink(f):
            all_files.append(f)
            if context is None:
                if "insights_commands" in f:
                    context = HostArchiveContext
                elif "sos_commands" in f:
                    context = SosArchiveContext
                elif "JBOSS_HOME" in f:
                    context = JDRContext

    context = context or HostArchiveContext
    common_path = os.path.commonprefix(all_files)
    if context is not ClusterArchiveContext:
        real_root = os.path.join(path, common_path)
    else:
        real_root = path
    return context(real_root, all_files=all_files)


def hydrate_new_dir(path, broker=None):
    broker = broker or dr.Broker()
    for root, dirs, names in os.walk(path):
        for name in names:
            p = os.path.join(root, name)
            with open(p) as f:
                serde.hydrate(serde.ser.load(f), broker)
    return SingleEvaluator(broker=broker)
