"""
Custom datasource to collect rootless podman containers from individual users.

``insights-client`` runs as root and therefore only sees root-owned podman
containers. This datasource discovers local users that have a rootless podman
storage directory and collects each user's
``podman ps --all --no-trunc --format=json`` output.
"""

import json
import logging
import os
import re
import signal

from typing import List

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, foreach_execute, simple_file
from insights.specs import Specs
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT
from insights.specs.datasources.user_group import all_users

ROOTLESS_STORAGE_SUBPATH = ".local/share/containers/storage"
""" str: Default rootless podman graphroot, relative to the user's home. """

_OCTAL_ESCAPE = re.compile(r"\\([0-7]{3})")

logger = logging.getLogger(__name__)


def _unescape_mountinfo_field(field):
    r"""Decode the kernel's octal escapes in mountinfo paths (``\040`` is a space)."""
    return _OCTAL_ESCAPE.sub(lambda m: chr(int(m.group(1), 8)), field)


def _normalize_path(path):
    """
    Wrapper around ``normpath`` to normalize ``path`` without touching
    the filesystem (text only) to prevent ``autofs`` mount.

    Converts a leading ``//`` to ``/`` which ``normpath`` keeps.
    """
    path = os.path.normpath(path)
    if path.startswith("//"):
        path = "/" + path.lstrip("/")
    return path


def _parse_mount_table(lines):
    """
    Map each mount point in ``/proc/self/mountinfo`` to the set of filesystem
    types mounted there, or None if nothing could be parsed.

    - Autofs direct mount maps a real filesystem on top of existing autofs
      filesystem.
    - Lines are split on ``" "``, not ``str.split()``, which would also cut a
      mount point at a no-break space.
    - Mount points are decoded like ``pw_dir`` (filesystem encoding) so they
      compare equal whatever the locale.
    """
    mount_dict = dict()
    for line in lines:
        mount_entry = line.split(" ")
        try:
            mount_point_escaped = _unescape_mountinfo_field(mount_entry[4])
            mount_point = _normalize_path(
                os.fsdecode(mount_point_escaped.encode("utf-8", "surrogateescape"))
            )
            # Since (counting from 0) the 6th field (i.e optional field) can
            # occur zero or more times, we use separator to determine the
            # filesystem type field.
            separator = mount_entry.index("-", 6)
            fs_type = mount_entry[separator + 1]
        except (ValueError, IndexError):
            continue

        mount_dict.setdefault(mount_point, set()).add(fs_type)

    return mount_dict or None


def _parent_mount_is_autofs(path, mount_table):
    """
    Return True if the most specific mount covering ``path`` is autofs only.

    Walks up from ``path`` and stops at the first mount point. A real
    filesystem stacked on autofs means the home is already mounted, so the
    result is False, as it is when no mount covers the path.

    Only the path text is used: ``stat`` or ``realpath`` would themselves
    trigger the automount this check avoids.

    Known limits (a mount hidden by a later one is still listed and used):

    - a symlinked home into autofs is not recognised, so it is checked
    - autofs mounted over a regular mount: the home is checked
    - regular mount over a parent of an autofs mount: the home is skipped
    """
    path = _normalize_path(path)
    while True:
        fs_types = mount_table.get(path)
        if fs_types is not None:
            return fs_types == {"autofs"}
        parent = os.path.dirname(path)
        if parent == path:
            # reached the top ("/" or "") without finding a covering mount
            return False
        path = parent


def _get_rootless_podman_users(entries, mount_table) -> List[str]:
    """
    Return sorted usernames (excluding root) that have a rootless podman storage
    directory under their home. No shell filter is applied: rootless service
    users commonly have a nologin shell.

    Username safety validation is handled upstream by the ``all_users``
    datasource via :func:`~insights.specs.datasources.is_safe_username`.

    Users whose storage path is under an unmounted autofs home are skipped,
    as checking it would make the automounter mount every such home (see
    :func:`_parent_mount_is_autofs`). They are therefore not reported.

    Args:
        entries: Passwd entries as returned by the ``all_users`` datasource.
        mount_table: Output of ``_parse_mount_table``.
    """
    users = set()
    skipped = 0
    for entry in entries:
        name = entry.pw_name
        home = entry.pw_dir
        if name == "root" or not home or home == "/":
            continue
        storage = os.path.join(home, ROOTLESS_STORAGE_SUBPATH)
        if _parent_mount_is_autofs(storage, mount_table):
            skipped += 1
            continue
        try:
            if os.path.isdir(storage):
                users.add(name)
        except OSError:
            continue
    if skipped:
        # count only: usernames and home paths may be PII
        logger.debug(
            "Skipped the rootless podman storage check for %d user(s) whose home "
            "is under an unmounted autofs mount",
            skipped,
        )
    return sorted(users)


class LocalSpecsMountinfo(Specs):
    """
    Local spec used only to read the mount table, so it is never archived.

    It is a separate class because ``LocalSpecs`` below depends on
    ``podman_rootless_users`` which depends on mountinfo.
    """

    mountinfo_local = simple_file("/proc/self/mountinfo", context=HostContext)


def _get_mount_table(broker):
    """Return the mount table read from ``/proc/self/mountinfo``, or None if unavailable."""
    mountinfo = broker.get(LocalSpecsMountinfo.mountinfo_local)
    if mountinfo is None:
        return None
    try:
        return _parse_mount_table(mountinfo.content)
    except Exception:
        # loading the content may raise OSError, ContentException, ...
        return None


@datasource(all_users, HostContext, LocalSpecsMountinfo.mountinfo_local)
def podman_rootless_users(broker) -> List[str]:
    """
    list: Users that have a rootless podman storage directory.

    The mountinfo spec is required. Without it autofs homes cannot be told
    apart, and checking every home would mount all of them, so the datasource
    is skipped instead.

    Raises:
        SkipComponent: When the mount table is unusable or no user is found.
    """
    mount_table = _get_mount_table(broker)
    if mount_table is None:
        raise SkipComponent("Could not read the mount information, not checking any home")
    users = _get_rootless_podman_users(broker[all_users], mount_table)
    if not users:
        raise SkipComponent("No users with rootless podman storage found")
    return users


class LocalSpecs(Specs):
    """Local specs used only by the rootless podman datasource."""

    podman_ps_rootless_raw = foreach_execute(
        podman_rootless_users,
        "/usr/sbin/runuser -s /bin/bash %s -c 'cd && /usr/bin/podman ps --all --no-trunc --format=json'",
        keep_rc=True,
        timeout=DEFAULT_SHELL_TIMEOUT,
        signum=signal.SIGTERM,
    )


@datasource(LocalSpecs.podman_ps_rootless_raw, HostContext)
def podman_ps_all_json_rootless(broker) -> DatasourceProvider:
    """
    Aggregate each user's rootless ``podman ps --all --no-trunc --format=json``
    output into one flat list of containers. The ``Labels`` key is dropped from
    every container because it may hold sensitive information. The owning
    username is used only to run the per-user command and is deliberately not
    persisted (it may be PII).

    Returns:
        DatasourceProvider: content is ``[<podman json without Labels>, ...]``.

    Raises:
        SkipComponent: When no rootless container data is available.
    """
    result = []  # type: List[dict]
    for item in broker[LocalSpecs.podman_ps_rootless_raw]:
        try:
            containers = json.loads("\n".join(item.content))
        except ValueError:
            continue
        # ``podman ps --format=json`` should yield a list of container dicts, but
        # a valid-but-unexpected shape (e.g. ``null`` or a single object) from one
        # user must not abort aggregation for everyone else.
        if not isinstance(containers, list):
            continue
        containers = [c for c in containers if isinstance(c, dict)]
        for container in containers:
            # Labels may contain sensitive information; never persist them.
            container.pop("Labels", None)
        if containers:
            result.extend(containers)
    if not result:
        raise SkipComponent("No rootless podman containers found")
    return DatasourceProvider(
        content=json.dumps(result),
        relative_path="insights_datasources/podman_ps_all_json_rootless",
        ds=Specs.podman_ps_all_json_rootless,
        ctx=broker.get(HostContext),
        cleaner=broker.get("cleaner"),
    )
