import pytest
from insights.util.file_permissions import FilePermissions
from insights.core import FileListing
from insights.tests import test_file_listing, context_wrap

PERMISSIONS_TEST_EXCEPTION_VECTORS = [
    ('-rw------ 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', True),
    ('bash: ls: command not found', True),
    ('-rw------ 1 root root 762 Se', True),
    ('-rw------- 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', False),
    ('-rw-------. 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', False),
    ('-rw-------@ 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', False),
    ('-rw-------+ 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', False),
    ('-rw-------* 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', False),
    ('-rw-------asdf 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', False),
    ('-rw------- 1 ro:t root 762 Sep 23 002 /etc/ssh/sshd_config', True),
    ('-rw------- 1 root r:ot 762 Sep 23 002 /etc/ssh/sshd_config', True),
    ('-rwasdfas- 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', True),
    ('-rwx/----- 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', True),
    ('/usr/bin/ls: cannot access /boot/grub2/grub.cfg: No such file or directory', True),
    ('cannot access /boot/grub2/grub.cfg: No such file or directory', True),
    ('No such file or directory', True),
    ('adsf', True),
]

PERMISSIONS_TEST_VECTORS = [
    ('-rw------- 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', False,
     'rw-', '---', '---', 'root', 'root', '/etc/ssh/sshd_config',
     True, True,
     True, True),
    ('-rw------- 1 root root 762 Sep 23 002 /a path/with/spaces everywhere', False,
     'rw-', '---', '---', 'root', 'root', '/a path/with/spaces everywhere',
     True, True,
     True, True),
    ('-rw------- 1 root root 762 Sep 23 002 no_slash_here', False,
     'rw-', '---', '---', 'root', 'root', 'no_slash_here',
     True, True,
     True, True),
    ('-rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config', False,
     'rw-', '---', '---', 'root', 'root', '/etc/ssh/sshd_config',
     True, True,
     True, True),
    ('-rw-rw-rw-. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config', False,
     'rw-', 'rw-', 'rw-', 'root', 'root', '/etc/ssh/sshd_config',
     True, True,
     False, False),
    ('-rw-rw---- 1 root user 762 Sep 23 002 /etc/ssh/sshd_config', True,
     'rw-', 'rw-', '---', 'root', 'user', '/etc/ssh/sshd_config',
     True, False,
     False, False),
    ('-rw------- 1 root user 762 Sep 23 002 /etc/ssh/sshd_config', False,
     'rw-', '---', '---', 'root', 'user', '/etc/ssh/sshd_config',
     True, False,
     True, True),
    ('-rw------- 1 user root 762 Sep 23 002 /etc/ssh/sshd_config', False,
     'rw-', '---', '---', 'user', 'root', '/etc/ssh/sshd_config',
     False, False,
     False, False),
    ('-rw-rw---- 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', True,
     'rw-', 'rw-', '---', 'root', 'root', '/etc/ssh/sshd_config',
     True, True,
     True, True),
    ('-rw-rw-r-- 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', True,
     'rw-', 'rw-', 'r--', 'root', 'root', '/etc/ssh/sshd_config',
     True, True,
     False, True),
    ('-rw-rw--w- 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', True,
     'rw-', 'rw-', '-w-', 'root', 'root', '/etc/ssh/sshd_config',
     True, True,
     True, False),
    ('---------- 1 root root 762 Sep 23 002 /etc/ssh/sshd_config', False,
     '---', '---', '---', 'root', 'root', '/etc/ssh/sshd_config',
     True, True,
     True, True),
]


def test_permissions():
    for vector in PERMISSIONS_TEST_VECTORS:
        (line, with_group,
         permissions_owner, permissions_group, permissions_other, owner, group, path,
         owned_by_root_user, owned_by_root_user_and_group,
         only_root_can_read, only_root_can_write) = vector
        p = FilePermissions(line)
        assert p.perms_owner == permissions_owner
        assert p.perms_group == permissions_group
        assert p.perms_other == permissions_other
        assert p.owner == owner
        assert p.group == group
        assert p.owned_by('root', also_check_group=False) == owned_by_root_user
        assert p.owned_by('root', also_check_group=True) == owned_by_root_user_and_group
        assert p.only_root_can_read(root_group_can_read=with_group) == only_root_can_read
        assert p.only_root_can_write(root_group_can_write=with_group) == only_root_can_write
        assert p.all_zero() == all((p.perms_owner == '---', p.perms_group == '---',
                                    p.perms_other == '---'))
        assert p.owner_can_read() == ('r' in p.perms_owner)
        assert p.owner_can_write() == ('w' in p.perms_owner)
        assert p.owner_can_only_read() == ('r--' == p.perms_owner)
        assert p.group_can_read() == ('r' in p.perms_group)
        assert p.group_can_write() == ('w' in p.perms_group)
        assert p.group_can_only_read() == ('r--' == p.perms_group)
        assert p.others_can_read() == ('r' in p.perms_other)
        assert p.others_can_write() == ('w' in p.perms_other)
        assert p.others_can_only_read() == ('r--' == p.perms_other)


def test_permissions_invalid():
    for vector in PERMISSIONS_TEST_EXCEPTION_VECTORS:
        garbage, should_raise = vector
        if should_raise:
            with pytest.raises(ValueError):
                FilePermissions(garbage)
        else:
            # shouldn't raise an exception
            FilePermissions(garbage)


def test_multiple_directories():
    dirs = FileListing(context_wrap(test_file_listing.MULTIPLE_DIRECTORIES))
    assert '/etc/sysconfig' in dirs
    assert 'cbq' in dirs.dirs_of('/etc/sysconfig')
    # drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq
    obj = FilePermissions.from_dict(dirs.path_entry('/etc/sysconfig/cbq'))
    assert hasattr(obj, 'name')
    assert obj.name == 'cbq'
    assert obj.perms_owner == 'rwx'
    assert obj.perms_group == 'r-x'
    assert obj.perms_other == 'r-x'
