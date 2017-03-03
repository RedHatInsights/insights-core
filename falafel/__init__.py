import pkgutil
from .core import Scannable, LogFileOutput, Mapper, IniConfigFile  # noqa: F401
from .core import FileListing, LegacyItemAccess, SysconfigOptions  # noqa: F401
from .core.plugins import mapper, reducer, make_response, make_metadata  # noqa: F401
from .mappers import get_active_lines  # noqa: F401
from .util import defaults, parse_table  # noqa: F401


package_info = {k: None for k in ["RELEASE", "COMMIT", "VERSION", "NAME"]}


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
