"""
Custom datasource for checking non-root owned packaged directories

Author: Florian Festi <ffesti@redhat.com>
"""
import grp
import json
import pwd
import stat

from insights import datasource
from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider


def get_shells():
    with open('/etc/shells') as f:
        return set((line.strip() for line in f))


def get_users():
    shells = get_shells()
    users = set()

    for user in pwd.getpwall():
        shell = user[6].strip()
        if shell not in shells or shell in ('/sbin/nologin', '/bin/nologin'):
            continue
        users.add(user[0])
    users.discard("root")
    return users


def get_groups(users):
    groups = set()

    for group in grp.getgrall():
        name = group[0]
        if name in users:
            groups.add(name)  # group for an user of interest
        for u in group[3]:
            u = u.strip()
            if u in users:
                groups.add(name)  # add groups containing a user
    return groups


@datasource()
def system_user_dirs(_broker):
    try:
        import rpm
    except ImportError:
        raise SkipComponent

    users = get_users()
    groups = get_groups(users)

    ts = rpm.TransactionSet()

    directories = {}
    for hdr in ts.dbMatch(rpm.RPMTAG_NAME):
        for f in rpm.files(hdr):
            if stat.S_ISDIR(f.mode):
                if ((f.user in users) and (f.mode & stat.S_IWUSR) or
                        (f.group in groups) and (f.mode & stat.S_IWGRP) or
                        (f.mode & stat.S_IWOTH)):
                    directories[f.name] = (hdr.NEVRA,)

    packages = {}
    for dirname, data in directories.items():
        mi = ts.dbMatch(rpm.RPMTAG_DIRNAMES, dirname + '/')
        for hdr in mi:
            packages.setdefault(hdr.NEVRA, []).append(dirname)

    return DatasourceProvider(content=json.dumps(packages), relative_path='insights_commands/system_user_dirs')
