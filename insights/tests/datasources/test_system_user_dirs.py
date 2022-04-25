"""
Tests for custom datasource for checking non-root owned packaged directories

Author: Florian Festi <ffesti@redhat.com>
"""
import mock

from insights.core.dr import SkipComponent
from insights.specs.datasources import system_user_dirs

try:
    import rpm
except ImportError:
    raise SkipComponent


def get_users():
    return set(["danger", "close"])


def get_groups(users):
    return set(["danger", "close"])


class TransactionSet:

    def _create_hdr(self):
        hdr = rpm.hdr()
        hdr["name"] = "testpkg"
        hdr["version"] = "1.0"
        hdr["release"] = "42"
        hdr["basenames"] = ["foo", "bar"]
        hdr["dirnames"] = ["/opt/", "/opt/foo/"]
        hdr["dirindexes"] = [0, 1]
        hdr["fileusername"] = ["danger", "danger"]
        hdr["filegroupname"] = ["danger", "danger"]
        hdr["filemodes"] = [0o040775, 0o100775]

        return hdr

    def __init__(self):
        self.hdrs = [self._create_hdr()]

    def dbMatch(self, *l):
        return self.hdrs


@mock.patch("insights.specs.datasources.system_user_dirs.get_users", get_users)
@mock.patch("insights.specs.datasources.system_user_dirs.get_groups", get_groups)
@mock.patch("rpm.TransactionSet", TransactionSet)
def test_system_user_dirs():
    result = system_user_dirs.system_user_dirs(None)
    assert result.content == ['{"testpkg-1.0-42.src": ["/opt/foo"]}']
