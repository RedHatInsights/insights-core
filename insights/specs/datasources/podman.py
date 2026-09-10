"""
Custom datasource to collect rootless podman containers from individual users.

``insights-client`` runs as root and therefore only sees root-owned podman
containers. This datasource discovers local users that have a rootless podman
storage directory and collects each user's
``podman ps --all --no-trunc --format=json`` output.
"""

import json
import os
import signal

from typing import List

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, foreach_execute
from insights.specs import Specs
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT, is_safe_username
from insights.specs.datasources.user_group import all_users

ROOTLESS_STORAGE_SUBPATH = ".local/share/containers/storage"
""" str: Default rootless podman graphroot, relative to the user's home. """


def _get_rootless_podman_users(entries) -> List[str]:
    """
    Return sorted usernames (excluding root) that have a rootless podman storage
    directory under their home. No shell filter is applied: rootless service
    users commonly have a nologin shell.

    Args:
        entries: Passwd entries as returned by ``pwd.getpwall()``.
    """
    users = set()
    for entry in entries:
        name = entry.pw_name
        home = entry.pw_dir
        if name == "root" or not home or home == "/":
            continue
        # The username is later interpolated into a command run as root; drop
        # any name that could forge extra argv tokens (argument injection).
        if not is_safe_username(name):
            continue
        storage = os.path.join(home, ROOTLESS_STORAGE_SUBPATH)
        try:
            if os.path.isdir(storage):
                users.add(name)
        except OSError:
            continue
    return sorted(users)


@datasource(all_users, HostContext)
def podman_rootless_users(broker) -> List[str]:
    """list: Users that have a rootless podman storage directory."""
    users = _get_rootless_podman_users(broker[all_users])
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
