"""
Custom datasource for CVE-2021-35937, CVE-2021-35938, and CVE-2021-35939.
"""

import grp
import pwd
import signal

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """
    Local spec used only by the rpm_pkgs datasource.
    """
    rpm_args = simple_command(
        'rpm -qa --nosignature --qf="[%{=NAME}; %{FILENAMES}; %{FILEMODES:perms}; %{FILEUSERNAME}; %{FILEGROUPNAME}\n]"',
        signum=signal.SIGTERM
    )


def get_shells():
    """
    Returns all full pathnames of valid login shells without nologins.
    """
    with open("/etc/shells") as file:
        return set(line.strip() for line in file if "nologin" not in line)


def get_users():
    """
    Returns all users with shell specified in get_shells() except for root.
    """
    shells = get_shells()
    users = set()

    for user in pwd.getpwall():
        name = user[0]
        shell = user[6]

        if name == "root" or (shell not in shells):
            continue
        users.add(name)
    return users


def get_groups(users):
    """
    Returns all groups for users specified in get_users().
    Every user has at least one group with its name.
    """
    groups = set()

    for group in grp.getgrall():
        group_name = group[0]
        user_list = group[3]

        if group_name in users:
            groups.add(group_name)
        else:
            for user in user_list:
                if user.strip() in users:
                    groups.add(group_name)
                    break
    return groups


@datasource(LocalSpecs.rpm_args, HostContext)
def pkgs_with_writable_dirs(broker):
    r"""
    Custom datasource for CVE-2021-35937, CVE-2021-35938, and CVE-2021-35939.

    It collects package names from the ``rpm -qa --nosignature --qf="[%{=NAME}; %{FILENAMES};
    %{FILEMODES:perms}; %{FILEUSERNAME}; %{FILEGROUPNAME}\n]" command``.

    The output is a sorted list of all packages, which have at least one directory with files
    inside, and this directory is writable by a specific user/group or the others.

    Raises:
        SkipComponent: Raised if no data is available

    Returns:
        List[str]: Sorted list of package names
    """
    content = broker[LocalSpecs.rpm_args].content

    if not content or "command not found" in content[0]:
        raise SkipComponent

    users = get_users()
    groups = get_groups(users)

    dir_package = {}
    dirs = set()

    for line in content:
        pkg_name, path_name, perms, user, group = line.split("; ")
        if perms[0] == "d":
            user_w = user in users and perms[2] == "w"
            group_w = group in groups and perms[5] == "w"
            others_w = perms[8] == "w"
            if user_w or group_w or others_w:
                # Stores a writeable directory with its package
                dir_package[path_name] = pkg_name
        else:
            # Stores a file directory for all files
            dirs.add(path_name.rsplit('/', 1)[0])

    # Stores a package if its associated file is in a writable directory
    packages = set(dir_package[dir] for dir in dirs if dir in dir_package)

    if packages:
        return DatasourceProvider(
            content=sorted(packages), relative_path="insights_commands/rpm_pkgs"
        )
