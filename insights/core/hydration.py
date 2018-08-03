import logging
import os

from glob import glob

from insights.core import archives, dr, serde
from insights.core.archives import COMPRESSION_TYPES
from insights.core.context import ClusterArchiveContext, JDRContext, HostArchiveContext, SerializedArchiveContext, SosArchiveContext
from insights.core.spec_factory import FileProvider

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
        if "insights_archive.txt" in f:
            return SerializedArchiveContext
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


def initialize_broker(ctx, broker=None):
    broker = broker or dr.Broker()
    cls = ctx.__class__
    if cls != SerializedArchiveContext:
        broker[cls] = ctx
        return broker

    raw_data = os.path.join(ctx.root, "raw_data")

    def localize(comp):
        def inner(thing):
            if isinstance(comp, FileProvider):
                comp.root = raw_data

        if isinstance(comp, list):
            for c in comp:
                inner(c)
        else:
            inner(comp)

    data = os.path.join(ctx.root, "data")
    for path in glob(os.path.join(data, "*")):
        with open(path) as f:
            doc = serde.ser.load(f)
        name = doc["name"]
        key = dr.get_component(name)
        broker.exec_times[key] = doc["time"]

        results = serde.unmarshal(doc["results"])
        if results:
            localize(results)
            broker[key] = results

        errors = serde.unmarshal(doc["errors"])
        if errors:
            broker.exceptions[key] = errors
    return broker
