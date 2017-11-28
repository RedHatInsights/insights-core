import pkgutil
from .core import Scannable, LogFileOutput, Parser, IniConfigFile  # noqa: F401
from .core import FileListing, LegacyItemAccess, SysconfigOptions  # noqa: F401
from .core import YAMLParser  # noqa: F401
from .core import AttributeDict  # noqa: F401
from .core import fava  # noqa: F401
from .core import SkipComponent  # noqa: F401
from .core import Syslog  # noqa: F401
from .core.plugins import parser, rule, make_response, make_metadata  # noqa: F401
from .parsers import get_active_lines  # noqa: F401
from .util import defaults  # noqa: F401
from .parsers import parse_delimited_table as parse_table  # noqa: F401


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
