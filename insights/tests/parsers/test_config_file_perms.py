import doctest
import pytest

from insights.parsers import config_file_perms
from insights.parsers.config_file_perms import SshdConfigPerms, Grub1ConfigPerms, Grub2ConfigPerms
from insights.tests import context_wrap


PARSERS = [
    # (parser class, path to configuration file)
    (SshdConfigPerms, "/etc/ssh/sshd_config"),
    (Grub1ConfigPerms, "/boot/grub/grub.conf"),
    (Grub2ConfigPerms, "/boot/grub2/grub.cfg")
]

TEST_CASES_PERMISSIONS = [
    # (line, owned_by_root, only_root_can_write)
    ('-rw-rw-r--. 1 root root 4179 Dec  1  2014 ', True, True),
    ('-rw-r--rw-. 1 root root 4179 Dec  1  2014 ', True, False),
    ('-rw-r--r--. 1 root user 4179 Dec  1  2014 ', False, True),
    ('-rw-rw-r--. 1 root user 4179 Dec  1  2014 ', False, False),
    ('-rw-r--r--. 1 user root 4179 Dec  1  2014 ', False, False),
]


@pytest.mark.parametrize("parser, path", PARSERS)
@pytest.mark.parametrize("line, owned_by_root, only_root_can_write", TEST_CASES_PERMISSIONS)
def test_sshd_grub(parser, path, line, owned_by_root, only_root_can_write):
    line_with_path = line + path
    result = parser(context_wrap(line_with_path))
    assert result.line == line_with_path
    assert result.owned_by("root", also_check_group=True) == owned_by_root
    assert result.only_root_can_write() == only_root_can_write


def test_doc_examples():
    sshd = "-rw-------. 1 root root 4179 Dec  1  2014 /etc/ssh/sshd_config"
    grub1 = "-rw-r--r--. 1 root root 4179 Dec  1  2014 /boot/grub/grub.conf"
    grub2 = "-rw-r--r--. 1 root root 4179 Dec  1  2014 /boot/grub2/grub.cfg"

    env = {
        "sshd_perms": SshdConfigPerms(context_wrap(sshd)),
        "grub1_perms": Grub1ConfigPerms(context_wrap(grub1)),
        "grub2_perms": Grub2ConfigPerms(context_wrap(grub2)),
    }
    failed, total = doctest.testmod(config_file_perms, globs=env)
    assert failed == 0
