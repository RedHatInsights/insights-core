import os
import pkgutil
from .config.factory import get_config  # noqa: F401
from .core import Scannable, LogFileOutput, Parser, IniConfigFile  # noqa: F401
from .core import FileListing, LegacyItemAccess, SysconfigOptions  # noqa: F401
from .core import YAMLParser                                       # noqa: F401
from .core import AttributeDict  # noqa: F401
from .core import Syslog  # noqa: F401
from .core import archives  # noqa: F401
from .core import dr  # noqa: F401
from .core.context import HostContext, HostArchiveContext  # noqa: F401
from .core.plugins import combiner, metadata, parser, rule  # noqa: F401
from .core.plugins import datasource, condition, incident  # noqa: F401
from .core.plugins import make_response, make_metadata  # noqa: F401
from .core.filters import add_filter, apply_filters, get_filters  # noqa: F401
from .parsers import get_active_lines  # noqa: F401
from .util import defaults  # noqa: F401

try:
    from .core import fava  # noqa: F401
except ImportError:
    pass


package_info = dict((k, None) for k in ["RELEASE", "COMMIT", "VERSION", "NAME"])


for name in package_info:
    package_info[name] = pkgutil.get_data(__name__, name).strip()


def get_nvr():
    return "{0}-{1}-{2}".format(package_info["NAME"],
                                package_info["VERSION"],
                                package_info["RELEASE"])


RULES_STATUS = {}
"""
Mapping of dictionaries containing nvr and commitid for each rule repo included
in this instance

{"rule_repo_1": {"version": nvr(), "commit": sha1}}
"""


def add_status(name, nvr, commit):
    """
    Rule repositories should call this method in their package __init__ to
    register their version information.
    """
    RULES_STATUS[name] = {"version": nvr, "commit": commit}


def run(root=None, component=None):
    """
    run is a general interface that is meant for stand alone scripts to use
    when executing insights components.

    Args:
        root (str): None will causes a host collection in which command and
            file specs are run. A directory or archive path will cause
            collection from the directory or archive, and only file type specs
            or those that depend on `insights.core.context.HostArchiveContext`
            will execute.
        component (function or class): The component to execute. Will only execute
            the component and its dependency graph. If None, all components with
            met dependencies will execute.

    Returns:
        broker: object containing the result of the evaluation.
    """
    if component:
        graph = dr.get_dependency_graph(component)
    else:
        graph = dr.COMPONENTS[dr.GROUPS.single]

    broker = dr.Broker()

    if not root:
        broker[HostContext] = HostContext()
        return dr.run(graph, broker=broker)

    if os.path.isdir(root):
        broker[HostArchiveContext] = HostArchiveContext(root=root)
        return dr.run(graph, broker=broker)

    extractor = archives.TarExtractor()
    with extractor.from_path(root) as ex:
        all_files = archives.get_all_files(ex.tmp_dir)
        common_path = os.path.commonprefix(all_files)
        real_root = os.path.join(ex.tmp_dir, common_path)
        broker[HostArchiveContext] = HostArchiveContext(root=real_root)
        return dr.run(graph, broker=broker)
