import os
from .core import LogFileOutput, Mapper, IniConfigFile, LegacyItemAccess  # noqa: F401
from .core import FileListing  # noqa: F401
from .core.plugins import mapper, reducer, make_response, make_metadata  # noqa: F401
from .mappers import get_active_lines  # noqa: F401
from .util import defaults, parse_table  # noqa: F401

__here__ = os.path.dirname(os.path.abspath(__file__))

package_info = {k: None for k in ["RELEASE", "COMMIT", "VERSION", "NAME"]}

for name in package_info:
    with open(os.path.join(__here__, name)) as f:
        package_info[name] = f.read().strip()


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
