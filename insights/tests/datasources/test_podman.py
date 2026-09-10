import json
import pwd

import pytest

from unittest.mock import Mock, patch

from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.podman import (
    LocalSpecs,
    _get_rootless_podman_users,
    podman_ps_all_json_rootless,
    podman_rootless_users,
)
from insights.specs.datasources.user_group import all_users

RELATIVE_PATH = "insights_datasources/podman_ps_all_json_rootless"


def _pw(name, home):
    # pwd.struct_passwd((name, passwd, uid, gid, gecos, dir, shell))
    return pwd.struct_passwd((name, "x", 1000, 1000, "", home, "/sbin/nologin"))


ALICE_PS = '[{"Id": "a1", "Image": "img:1", "Names": ["foreman"], "State": "running"}]'
BOB_PS = '[{"Id": "b1", "Image": "img:2", "Names": ["receptor"], "State": "exited"}]'


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
    have_storage = {
        "/home/alice/.local/share/containers/storage",
        "/home/bob/.local/share/containers/storage",
    }
    isdir.side_effect = lambda p: p in have_storage
    assert _get_rootless_podman_users(entries) == ["alice", "bob"]


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_get_rootless_podman_users_drops_unsafe_names(isdir):
    # A crafted passwd entry whose name would forge extra argv tokens once the
    # runuser command is split must be dropped, even if it has a storage dir.
    entries = [
        _pw("alice", "/home/alice"),  # kept: safe name with storage
        _pw("root -c payload", "/home/evil"),  # dropped: unsafe name
    ]
    isdir.return_value = True  # both have a storage dir
    assert _get_rootless_podman_users(entries) == ["alice"]


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_podman_rootless_users(isdir):
    entries = [_pw("root", "/root"), _pw("alice", "/home/alice")]
    isdir.side_effect = lambda p: p == "/home/alice/.local/share/containers/storage"
    broker = {all_users: entries}
    assert podman_rootless_users(broker) == ["alice"]


@patch("insights.specs.datasources.podman.os.path.isdir")
def test_podman_rootless_users_skip_when_none(isdir):
    entries = [_pw("root", "/root"), _pw("carol", "/home/carol")]
    isdir.return_value = False
    broker = {all_users: entries}
    with pytest.raises(SkipComponent):
        podman_rootless_users(broker)


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
