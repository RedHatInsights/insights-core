import json
import logging
import os
import pwd

import pytest

from unittest.mock import Mock, PropertyMock, call, patch

from insights import dr
from insights.core.context import HostContext
from insights.core.exceptions import ContentException, SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.podman import (
    LocalSpecs,
    LocalSpecsMountinfo,
    _get_rootless_podman_users,
    _parent_mount_is_autofs,
    _parse_mount_table,
    _unescape_mountinfo_field,
    podman_ps_all_json_rootless,
    podman_rootless_users,
)
from insights.specs.datasources.user_group import all_users

RELATIVE_PATH = "insights_datasources/podman_ps_all_json_rootless"

ALICE_STORAGE = "/home/alice/.local/share/containers/storage"
BOB_STORAGE = "/home/bob/.local/share/containers/storage"
CAROL_STORAGE = "/srv/carol/.local/share/containers/storage"

TABLE_NO_AUTOFS = {"/": {"xfs"}}
TABLE_HOME_AUTOFS = {"/": {"xfs"}, "/home": {"autofs"}}


def _pw(name, home):
    # pwd.struct_passwd((name, passwd, uid, gid, gecos, dir, shell))
    return pwd.struct_passwd((name, "x", 1000, 1000, "", home, "/sbin/nologin"))


def _mountinfo(*lines):
    # stands in for the mountinfo provider, whose content is a list of lines
    return Mock(content=list(lines))


AUTOFS_MOUNTINFO = _mountinfo(
    "22 1 0:21 / / rw,relatime shared:1 - xfs /dev/mapper/rootvg-rootlv rw,attr2",
    "590 22 0:49 / /home rw,relatime shared:322 - autofs /etc/auto.home rw,fd=13,indirect",
    "61 590 0:45 /bob /home/bob rw,relatime master:2 - nfs4 server:/export/bob rw",
)


ALICE_PS = '[{"Id": "a1", "Image": "img:1", "Names": ["foreman"], "State": "running"}]'
BOB_PS = '[{"Id": "b1", "Image": "img:2", "Names": ["receptor"], "State": "exited"}]'


# --- _unescape_mountinfo_field ---------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("/plain/path", "/plain/path"),  # no escapes
        ("/a\\040b", "/a b"),  # space
        ("/a\\011b", "/a\tb"),  # tab
        ("/a\\012b", "/a\nb"),  # newline
        ("/a\\134b", "/a\\b"),  # backslash
        ("/tmp\\040\\040x", "/tmp  x"),  # consecutive escapes
        # an escaped backslash must not create a new escape
        ("/a\\134040", "/a\\040"),
    ],
)
def test_unescape_mountinfo_field(raw, expected):
    assert _unescape_mountinfo_field(raw) == expected


# --- _parse_mount_table ------------------------------------------------------


def test_parse_mount_table_parses_mount_points_and_fstypes():
    lines = [
        "22 1 0:21 / / rw,relatime shared:1 - xfs /dev/mapper/rootvg-rootlv rw,attr2",
        "39 22 8:1 / /boot rw,relatime shared:30 - xfs /dev/sda1 rw,attr2",
        "575 97 0:48 / /net rw,relatime shared:314 - autofs -hosts rw,fd=10,pgrp=1127,timeout=300,minproto=5,maxproto=5,indirect,pipe_ino=27553",
        "590 97 0:49 / /home rw,relatime shared:322 - autofs /etc/auto.home rw,fd=13,pgrp=1127,timeout=60,minproto=5,maxproto=5,indirect,pipe_ino=27555",
        "410 46 0:50 / /proc/sys/fs/binfmt_misc rw,relatime shared:216 - binfmt_misc binfmt_misc rw",
        "424 22 0:51 / /sys/fs/fuse/connections rw,relatime shared:224 - fusectl fusectl rw",
        "395 28 0:46 / /run/user/0 rw,nosuid,nodev,relatime shared:207 - tmpfs tmpfs rw,seclabel,size=130500k,mode=700",
        # the mount point is "/home/alice", not the root field "/alice"
        "61 47 0:45 /alice /home/alice rw,relatime master:2 - nfs4 server:/export/alice rw",
    ]
    assert _parse_mount_table(lines) == {
        "/": {"xfs"},
        "/boot": {"xfs"},
        "/net": {"autofs"},
        "/home": {"autofs"},
        "/proc/sys/fs/binfmt_misc": {"binfmt_misc"},
        "/sys/fs/fuse/connections": {"fusectl"},
        "/run/user/0": {"tmpfs"},
        "/home/alice": {"nfs4"},
    }


def test_parse_mount_table_handles_optional_fields():
    lines = [
        "22 1 0:21 / / rw - xfs /dev/sda1 rw",  # no optional fields
        "23 22 0:22 / /a rw shared:1 - ext4 /dev/sda2 rw",  # one optional field
        "24 22 0:23 / /b rw shared:1 master:2 propagate_from:3 - btrfs /dev/sda3 rw",  # several
    ]
    assert _parse_mount_table(lines) == {"/": {"xfs"}, "/a": {"ext4"}, "/b": {"btrfs"}}


def test_parse_mount_table_unescapes_mount_points():
    lines = [
        "65 22 8:17 / /run/media/root/VMware\\040Tools rw,relatime shared:72 - iso9660 /dev/sr0 ro",
        "66 22 253:6 / /data\\134backup rw,relatime shared:73 - ext4 /dev/mapper/vg-data rw",
    ]
    assert _parse_mount_table(lines) == {
        "/run/media/root/VMware Tools": {"iso9660"},
        "/data\\backup": {"ext4"},
    }


def test_parse_mount_table_unions_duplicate_mount_points():
    lines = [
        "100 47 0:38 / /home/alice rw,relatime shared:80 - autofs auto.home rw,indirect",
        "101 100 253:5 / /home/alice rw,relatime master:80 - ext4 /dev/mapper/vg-alice rw",
    ]
    assert _parse_mount_table(lines) == {"/home/alice": {"autofs", "ext4"}}


def test_parse_mount_table_skips_malformed_lines():
    lines = [
        "this line is not mountinfo",
        "1 2 3",
        "",
        "1 2 3 4 5 -",
        "22 1 0:21 / / rw,relatime - xfs /dev/mapper/rootvg-rootlv rw",
    ]
    assert _parse_mount_table(lines) == {"/": {"xfs"}}


@pytest.mark.parametrize("lines", [[], [""], ["garbage", "more garbage"]])
def test_parse_mount_table_returns_none_when_nothing_parses(lines):
    assert _parse_mount_table(lines) is None


def test_parse_mount_table_keeps_unicode_whitespace_inside_a_mount_point():
    # a no-break space (U+00A0) is part of the name; str.split() would cut the mount point there
    lines = ["22 1 0:21 / /home/a\u00a0b rw - autofs auto.home rw"]
    expected = os.fsdecode("/home/a\u00a0b".encode("utf-8"))  # same decoding as pw_dir
    assert _parse_mount_table(lines) == {expected: {"autofs"}}


def test_parse_mount_table_non_ascii_mount_point_matches_pw_dir():
    home = "/home/jos\u00e9"
    # the provider hands over UTF-8 text; pwd decodes pw_dir with the filesystem encoding
    mount_point = home.encode("utf-8").decode("utf-8", "surrogateescape")
    table = _parse_mount_table(["22 1 0:21 / %s rw - autofs auto.home rw" % mount_point])
    pw_dir = os.fsdecode(home.encode("utf-8"))
    assert _parent_mount_is_autofs(os.path.join(pw_dir, "x"), table) is True


def test_parse_mount_table_invalid_utf8_mount_point_does_not_raise():
    # the kernel writes raw bytes; an undecodable byte arrives as a lone surrogate
    lines = ["22 1 0:21 / /home/bad\udcff rw - autofs auto.home rw"]
    table = _parse_mount_table(lines)
    assert table == {os.fsdecode(b"/home/bad\xff"): {"autofs"}}


# --- _parent_mount_is_autofs -------------------------------------------------


@pytest.mark.parametrize(
    "table,path,expected",
    [
        (TABLE_HOME_AUTOFS, ALICE_STORAGE, True),
        ({**TABLE_HOME_AUTOFS, "/home/alice": {"nfs4"}}, ALICE_STORAGE, False),
        ({"/": {"xfs"}, "/home": {"xfs"}, "/home/alice": {"autofs"}}, ALICE_STORAGE, True),
        ({"/": {"xfs"}, "/home": {"xfs"}, "/home/alice": {"autofs", "ext4"}}, ALICE_STORAGE, False),
        ({"/": {"xfs"}, "/home": {"ext4"}}, ALICE_STORAGE, False),
        # /home/al is not a parent of /home/alice
        ({"/": {"xfs"}, "/home": {"xfs"}, "/home/al": {"autofs"}}, ALICE_STORAGE, False),
        ({"/": {"xfs"}, "/home": {"xfs"}, "/home/al": {"autofs"}}, "/home/al", True),
        # a mount point does not cover its own parent
        ({"/": {"xfs"}, "/home/alice": {"autofs"}}, "/home", False),
        (TABLE_NO_AUTOFS, "/var/lib/whatever", False),
        # a deeper autofs mount wins over shallower regular mounts
        (
            {"/": {"xfs"}, "/home": {"ext4"}, "/home/staff": {"autofs"}},
            "/home/staff/bob/.local/share/containers/storage",
            True,
        ),
        (
            {"/": {"xfs"}, "/home": {"ext4"}, "/home/staff": {"autofs"}},
            "/home/bob/.local/share/containers/storage",
            False,
        ),
        # no covering mount, an empty table and relative paths all return False
        ({"/home": {"autofs"}}, "/var/lib/whatever", False),
        ({}, ALICE_STORAGE, False),
        (TABLE_HOME_AUTOFS, "home/alice/.local/share/containers/storage", False),
        # redundant separators and "."/".." components are normalised away
        (TABLE_HOME_AUTOFS, "/home//alice/./.local/share/containers/storage", True),
        (TABLE_HOME_AUTOFS, "/home/alice/../alice/.local/share/containers/storage", True),
        # normalisation changes the verdict: without it the raw prefix is /home/alice (autofs)
        # in the first case and /home (autofs) in the second
        (
            {"/": {"xfs"}, "/home": {"xfs"}, "/home/alice": {"autofs"}},
            "/home/alice/../zoe/.local/share/containers/storage",
            False,
        ),
        (TABLE_HOME_AUTOFS, "/home/../var/lib/x", False),
        # Linux treats a leading "//" as "/"
        (TABLE_HOME_AUTOFS, "//home/alice/.local/share/containers/storage", True),
        (TABLE_HOME_AUTOFS, "///home/alice/.local/share/containers/storage", True),
        # the "/" mount alone decides when nothing deeper covers the path
        ({"/": {"autofs"}}, "/x/y", True),
        # the path is itself the mount point, or the filesystem root
        (TABLE_HOME_AUTOFS, "/home", True),
        (TABLE_HOME_AUTOFS, "/", False),
    ],
)
def test_parent_mount_is_autofs(table, path, expected):
    assert _parent_mount_is_autofs(path, table) is expected


def test_parent_mount_is_autofs_does_not_touch_the_filesystem():
    # stat/realpath on an unmounted autofs home would itself trigger the mount
    forbidden = (
        "os.stat",
        "os.lstat",
        "os.path.realpath",
        "os.path.exists",
        "os.path.lexists",
        "os.path.isdir",
        "os.listdir",
        "os.scandir",
    )
    patches = [
        patch(name, side_effect=AssertionError(name + " must not be called")) for name in forbidden
    ]
    for p in patches:
        p.start()
    try:
        assert _parent_mount_is_autofs(ALICE_STORAGE, TABLE_HOME_AUTOFS) is True
        assert _parent_mount_is_autofs(ALICE_STORAGE, TABLE_NO_AUTOFS) is False
    finally:
        for p in patches:
            p.stop()


# --- _get_rootless_podman_users ------------------------------------------------

@patch("insights.specs.datasources.podman.os.path.isdir")
def test_get_rootless_podman_users(isdir):
    entries = [
        _pw("root", "/root"),  # excluded: root
        _pw("alice", "/home/alice"),  # kept: has storage
        _pw("bob", "/home/bob"),  # kept: has storage
        _pw("carol", "/home/carol"),  # excluded: no storage dir
        _pw("daemon", "/"),  # excluded: home is /
        _pw("nohome", ""),  # excluded: no home
    ]
    have_storage = {ALICE_STORAGE, BOB_STORAGE}
    isdir.side_effect = lambda p: p in have_storage
    assert _get_rootless_podman_users(entries, mount_table=TABLE_NO_AUTOFS) == ["alice", "bob"]


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_get_rootless_podman_users_skips_unmounted_autofs_homes(isdir):
    entries = [
        _pw("alice", "/home/alice"),  # autofs home, not mounted
        _pw("bob", "/home/bob"),  # mounted home
        _pw("carol", "/srv/carol"),  # regular filesystem
    ]
    table = {
        "/": {"xfs"},
        "/home": {"autofs"},
        "/home/bob": {"nfs4"},
        "/srv": {"xfs"},
    }
    isdir.side_effect = lambda p: p == BOB_STORAGE

    assert _get_rootless_podman_users(entries, mount_table=table) == ["bob"]

    # exact calls, in order: alice's autofs home must never be probed
    assert isdir.call_args_list == [call(BOB_STORAGE), call(CAROL_STORAGE)]


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_get_rootless_podman_users_skip_log_has_no_usernames_or_paths(isdir, caplog):
    entries = [_pw("alice", "/home/alice"), _pw("bob", "/home/bob"), _pw("carol", "/srv/carol")]
    isdir.return_value = False
    with caplog.at_level(logging.DEBUG, logger="insights.specs.datasources.podman"):
        _get_rootless_podman_users(entries, mount_table=TABLE_HOME_AUTOFS)

    # one summary record with the count of skipped users (alice and bob)
    records = [r for r in caplog.records if r.name == "insights.specs.datasources.podman"]
    assert len(records) == 1
    message = records[0].getMessage()
    assert "2 user(s)" in message
    for pii in ("alice", "bob", "carol", "/home"):
        assert pii not in message


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_get_rootless_podman_users_direct_map_untriggered(isdir):
    entries = [_pw("alice", "/home/alice")]
    table = {"/": {"xfs"}, "/home": {"xfs"}, "/home/alice": {"autofs"}}
    assert _get_rootless_podman_users(entries, mount_table=table) == []
    isdir.assert_not_called()


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_get_rootless_podman_users_direct_map_triggered(isdir):
    entries = [_pw("alice", "/home/alice")]
    table = {"/": {"xfs"}, "/home": {"xfs"}, "/home/alice": {"autofs", "ext4"}}
    isdir.return_value = True
    assert _get_rootless_podman_users(entries, mount_table=table) == ["alice"]
    isdir.assert_called_once_with(ALICE_STORAGE)


# --- podman_rootless_users datasource -------------------------------------------

@patch("insights.specs.datasources.podman.os.path.isdir")
def test_podman_rootless_users(isdir):
    entries = [_pw("root", "/root"), _pw("alice", "/home/alice")]
    isdir.side_effect = lambda p: p == ALICE_STORAGE
    broker = {
        all_users: entries,
        LocalSpecsMountinfo.mountinfo_local: _mountinfo(
            "22 1 0:21 / / rw - xfs /dev/sda1 rw",
        ),
    }
    assert podman_rootless_users(broker) == ["alice"]


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_podman_rootless_users_skip_when_none(isdir):
    entries = [_pw("root", "/root"), _pw("carol", "/home/carol")]
    isdir.return_value = False
    broker = {
        all_users: entries,
        LocalSpecsMountinfo.mountinfo_local: _mountinfo("22 1 0:21 / / rw - xfs /dev/sda1 rw"),
    }
    with pytest.raises(SkipComponent):
        podman_rootless_users(broker)


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_podman_rootless_users_uses_mountinfo_to_skip_autofs_homes(isdir):
    entries = [_pw("alice", "/home/alice"), _pw("bob", "/home/bob"), _pw("carol", "/home/carol")]
    isdir.side_effect = lambda p: p == BOB_STORAGE
    broker = {all_users: entries, LocalSpecsMountinfo.mountinfo_local: AUTOFS_MOUNTINFO}
    assert podman_rootless_users(broker) == ["bob"]
    # alice and carol are unmounted autofs homes and must not be probed
    assert isdir.call_args_list == [call(BOB_STORAGE)]


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_podman_rootless_users_skips_all_autofs_homes_without_probing(isdir):
    entries = [_pw("alice", "/home/alice"), _pw("carol", "/home/carol")]
    isdir.side_effect = AssertionError("isdir must not be called for autofs homes")
    broker = {all_users: entries, LocalSpecsMountinfo.mountinfo_local: AUTOFS_MOUNTINFO}
    with pytest.raises(SkipComponent):
        podman_rootless_users(broker)
    assert isdir.call_args_list == []


def _raises(exc):
    provider = Mock()
    type(provider).content = PropertyMock(side_effect=exc)
    return provider


@pytest.mark.parametrize(
    "mountinfo",
    [
        pytest.param(None, id="spec-not-available"),
        pytest.param(_mountinfo(), id="empty"),
        pytest.param(_raises(ContentException("empty")), id="content-exception"),
        pytest.param(_raises(UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad")), id="decode-error"),
    ],
)
@patch("insights.specs.datasources.podman.os.path.isdir")
def test_podman_rootless_users_skips_when_mountinfo_unusable(isdir, mountinfo):
    # without a mount table every home would be probed, mounting all autofs homes
    entries = [_pw("alice", "/home/alice"), _pw("bob", "/home/bob")]
    isdir.side_effect = AssertionError("isdir must not be called without a mount table")
    broker = {all_users: entries}
    if mountinfo is not None:
        broker[LocalSpecsMountinfo.mountinfo_local] = mountinfo

    with pytest.raises(SkipComponent, match="mount information"):
        podman_rootless_users(broker)
    assert isdir.call_args_list == []


def test_podman_rootless_users_mountinfo_is_a_required_dependency():
    # optional would let the datasource run without it and probe, and so mount, every home
    delegate = dr.get_delegate(podman_rootless_users)
    assert LocalSpecsMountinfo.mountinfo_local in delegate.requires
    assert LocalSpecsMountinfo.mountinfo_local not in delegate.optional
    assert HostContext in delegate.requires


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_podman_rootless_users_end_to_end_from_raw_mountinfo(isdir):
    # raw mountinfo text, as read from the file, through the parser and the lookup to discovery
    mountinfo = _mountinfo(
        "22 1 0:21 / / rw,relatime shared:1 - xfs /dev/mapper/rootvg-rootlv rw,attr2",
        # indirect map: /home is autofs, bob's home is currently mounted
        "590 22 0:49 / /home rw,relatime shared:322 - autofs /etc/auto.home rw,fd=13,indirect",
        "61 590 0:45 /bob /home/bob rw,relatime master:2 - nfs4 server:/export/bob rw",
        # direct map with an escaped space: dave is not mounted, eve is (autofs + ext4 stacked)
        "120 22 0:60 / /export/dave\\040home rw,relatime - autofs auto.direct rw,direct",
        "121 22 0:61 / /export/eve\\040home rw,relatime - autofs auto.direct rw,direct",
        "122 121 253:9 / /export/eve\\040home rw,relatime - ext4 /dev/mapper/vg-eve rw",
        # direct map with a non-ASCII name, not mounted
        "130 22 0:62 / /data/jos\u00e9 rw,relatime - autofs auto.direct rw,direct",
    )
    entries = [
        _pw("alice", "/home/alice"),  # under /home autofs, not mounted -> skipped
        _pw("bob", "/home/bob"),  # mounted -> probed
        _pw("carol", "/srv/carol"),  # regular filesystem -> probed
        _pw("dave", "/export/dave home"),  # untriggered direct map -> skipped
        _pw("eve", "/export/eve home"),  # triggered direct map -> probed
        _pw("jose", os.fsdecode("/data/jos\u00e9".encode("utf-8"))),  # non-ASCII -> skipped
        _pw("spaced", "/home/my user"),  # space in the name under /home autofs -> skipped
    ]
    eve_storage = "/export/eve home/.local/share/containers/storage"
    isdir.side_effect = lambda p: p in (BOB_STORAGE, eve_storage)

    assert podman_rootless_users(
        {all_users: entries, LocalSpecsMountinfo.mountinfo_local: mountinfo}
    ) == ["bob", "eve"]
    assert isdir.call_args_list == [call(BOB_STORAGE), call(CAROL_STORAGE), call(eve_storage)]


# --- podman_ps_all_json_rootless aggregation ------------------------------------

def test_podman_ps_all_json_rootless():
    alice = Mock()
    alice.args = "alice"
    alice.content = [ALICE_PS]
    bob = Mock()
    bob.args = "bob"
    bob.content = [BOB_PS]
    empty = Mock()
    empty.args = "carol"
    empty.content = ["[]"]  # no containers -> dropped
    broken = Mock()
    broken.args = "dave"
    broken.content = ["not json"]  # unparseable -> dropped

    broker = {LocalSpecs.podman_ps_rootless_raw: [alice, bob, empty, broken]}
    result = podman_ps_all_json_rootless(broker)

    assert isinstance(result, DatasourceProvider)
    assert result.relative_path == RELATIVE_PATH
    # flat list of containers, no per-user grouping and no username persisted
    expected = json.loads(ALICE_PS) + json.loads(BOB_PS)
    assert json.loads("".join(result.content)) == expected


def test_podman_ps_all_json_rootless_skips_bad_shapes():
    # A valid-but-unexpected JSON shape from one user (null, a single object, or
    # a list containing non-dicts) must be skipped, not abort aggregation for
    # the other users.
    null_out = Mock()
    null_out.args = "alice"
    null_out.content = ["null"]  # podman may emit null for "empty"
    single_obj = Mock()
    single_obj.args = "bob"
    single_obj.content = ['{"Id": "x", "Labels": {"s": 1}}']  # object, not a list
    dirty_list = Mock()
    dirty_list.args = "carol"
    dirty_list.content = ['[null, "str", {"Id": "c1", "Names": ["ok"]}]']  # mixed
    good = Mock()
    good.args = "dave"
    good.content = [ALICE_PS]

    broker = {LocalSpecs.podman_ps_rootless_raw: [null_out, single_obj, dirty_list, good]}
    result = podman_ps_all_json_rootless(broker)

    containers = json.loads("".join(result.content))
    # only the dict from the mixed list and the good user's container survive
    assert sorted(c["Id"] for c in containers) == ["a1", "c1"]


def test_podman_ps_all_json_rootless_skip_when_empty():
    empty = Mock()
    empty.args = "carol"
    empty.content = ["[]"]
    broker = {LocalSpecs.podman_ps_rootless_raw: [empty]}
    with pytest.raises(SkipComponent):
        podman_ps_all_json_rootless(broker)


def test_podman_ps_all_json_rootless_strips_labels():
    labeled = Mock()
    labeled.args = "alice"
    labeled.content = [
        '[{"Id": "a1", "Image": "img:1", "Names": ["foreman"], "State": "running",'
        ' "Labels": {"secret": "do-not-collect"}}]'
    ]
    broker = {LocalSpecs.podman_ps_rootless_raw: [labeled]}
    result = podman_ps_all_json_rootless(broker)

    containers = json.loads("".join(result.content))
    assert len(containers) == 1
    # Labels may hold sensitive data and must never be persisted
    assert "Labels" not in containers[0]
    # the rest of the container json is left intact
    assert containers[0]["Id"] == "a1"
    assert containers[0]["Names"] == ["foreman"]
