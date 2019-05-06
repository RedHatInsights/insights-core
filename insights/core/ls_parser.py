"""
This module contains logic for parsing ls output. It attempts to handle
output when selinux is enabled or disabled and also skip "bad" lines.
"""
import six


def parse_path(path):
    """
    Convert possible symbolic link into a source -> target pair.

    Args:
        path (str): The path portion of an ls output line.

    Returns:
        A (path, link) tuple where path is always populated and link is a non
        empty string if the original path is a symoblic link.
    """
    path, _, link = path.partition(" -> ")
    return path, link


def parse_non_selinux(parts):
    """
    Parse part of an ls output line that isn't selinux.

    Args:
        parts (list): A four element list of strings representing the initial
            parts of an ls line after the permission bits. The parts are link
            count, owner, group, and everything else.

    Returns:
        A dict containing links, owner, group, date, and name. If the line
        represented a device, major and minor numbers are included.  Otherwise,
        size is included. If the raw name was a symbolic link, link is
        included.
    """
    links, owner, group, last = parts
    result = {
        "links": int(links),
        "owner": owner,
        "group": group,
    }

    # device numbers only go to 256.
    # If a comma is in the first four characters, the next two elements are
    # major and minor device numbers. Otherwise, the next element is the size.
    if "," in last[:4]:
        major, minor, rest = last.split(None, 2)
        result["major"] = int(major.rstrip(","))
        result["minor"] = int(minor)
    else:
        size, rest = last.split(None, 1)
        result["size"] = int(size)

    # The date part is always 12 characters regardless of content.
    result["date"] = rest[:12]

    # Jump over the date and the following space to get the path part.
    path, link = parse_path(rest[13:])
    result["name"] = path
    if link:
        result["link"] = link

    return result


def parse_selinux(parts):
    """
    Parse part of an ls output line that is selinux.

    Args:
        parts (list): A four element list of strings representing the initial
            parts of an ls line after the permission bits. The parts are owner
            group, selinux info, and the path.

    Returns:
        A dict containing owner, group, se_user, se_role, se_type, se_mls, and
        name. If the raw name was a symbolic link, link is also included.

    """

    owner, group = parts[:2]
    selinux = parts[2].split(":")
    lsel = len(selinux)
    path, link = parse_path(parts[-1])
    result = {
        "owner": owner,
        "group": group,
        "se_user": selinux[0],
        "se_role": selinux[1] if lsel > 1 else None,
        "se_type": selinux[2] if lsel > 2 else None,
        "se_mls": selinux[3] if lsel > 3 else None,
        "name": path
    }
    if link:
        result["link"] = link
    return result


def parse_rhel8_selinux(parts):
    """
    Parse part of an ls output line that is selinux on RHEL8.

    Args:
        parts (list): A four element list of strings representing the initial
            parts of an ls line after the permission bits. The parts are link
            count, owner, group, and everything else

    Returns:
        A dict containing links, owner, group, se_user, se_role, se_type,
        se_mls, size, date, and name. If the raw name was a symbolic link,
        link is also included.

    """

    links, owner, group, last = parts

    selinux = parts[3].split(":")
    lsel = len(selinux)
    selinux, size, last = parts[-1].split(None, 2)
    selinux = selinux.split(":")
    date = last[:12]
    path, link = parse_path(last[13:])
    result = {
        "links": int(links),
        "owner": owner,
        "group": group,
        "se_user": selinux[0],
        "se_role": selinux[1] if lsel > 1 else None,
        "se_type": selinux[2] if lsel > 2 else None,
        "se_mls": selinux[3] if lsel > 3 else None,
        "size": int(size),
        "name": path,
        "date": date,
    }
    if link:
        result["link"] = link
    return result


PASS_KEYS = set(["name", "total"])
DELAYED_KEYS = ["entries", "files", "dirs", "specials"]


class Directory(dict):
    def __init__(self, name, total, body):
        data = dict.fromkeys(DELAYED_KEYS)
        data["name"] = name
        data["total"] = total
        self.body = body
        self.loaded = False
        super(Directory, self).__init__(data)

    def iteritems(self):
        if not self.loaded:
            self._load()
        return six.iteritems(super(Directory, self))

    def items(self):
        if not self.loaded:
            self._load()
        return super(Directory, self).items()

    def values(self):
        if not self.loaded:
            self._load()
        return super(Directory, self).values()

    def get(self, key, default=None):
        if not self.loaded:
            self._load()
        return super(Directory, self).get(key, default)

    def _load(self):
        dirs = []
        ents = {}
        files = []
        specials = []
        for line in self.body:
            # we can't split(None, 5) here b/c rhel 6/7 selinux lines only have
            # 4 parts before the path, and the path itself could contain
            # spaces. Unfortunately, this means we have to split the line again
            # below
            parts = line.split(None, 4)
            perms = parts[0]
            typ = perms[0]
            entry = {
                "type": typ,
                "perms": perms[1:]
            }
            if parts[1][0].isdigit():
                # We have to split the line again to see if this is a RHEL8
                # selinux stanza. This assumes that the context section will
                # always have at least two pieces separated by ':'.
                if ":" in line.split()[4]:
                    rest = parse_rhel8_selinux(parts[1:])
                else:
                    rest = parse_non_selinux(parts[1:])
            else:
                rest = parse_selinux(parts[1:])

            # Update our entry and put it into the correct buckets
            # based on its type.
            entry.update(rest)
            entry["raw_entry"] = line
            entry["dir"] = self["name"]
            nm = entry["name"]
            ents[nm] = entry
            if typ not in "bcd":
                files.append(nm)
            elif typ == "d":
                dirs.append(nm)
            elif typ in "bc":
                specials.append(nm)

        self.update({"entries": ents,
                     "files": files,
                     "dirs": dirs,
                     "specials": specials})

        self.loaded = True
        del self.body

    def __getitem__(self, key):
        if self.loaded or key in PASS_KEYS:
            return super(Directory, self).__getitem__(key)
        self._load()
        return super(Directory, self).__getitem__(key)


def parse(lines, root=None):
    """
    Parses a list of lines from ls into dictionaries representing their
    components.

    Args:
        lines (list): A list of lines generated by ls.
        root (str): The directory name to be used for ls output stanzas that
            don't have a name.

    Returns:
        A dictionary representing the ls output. It's keyed by the path
        containing each ls stanza.
    """
    doc = {}
    entries = []
    name = None
    total = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line and line[0] == "/" and line[-1] == ":":
            if name is None:
                name = line[:-1]
                if entries:
                    d = Directory(name, total or len(entries), entries)
                    doc[root] = d
                    total = None
                    entries = []
            else:
                d = Directory(name, total or len(entries), entries)
                doc[name or root] = d
                total = None
                entries = []
                name = line[:-1]
            continue
        if line.startswith("total"):
            total = int(line.split(None, 1)[1])
            continue
        entries.append(line)
    name = name or root
    total = total if total is not None else len(entries)
    doc[name] = Directory(name, total, entries)
    return doc
