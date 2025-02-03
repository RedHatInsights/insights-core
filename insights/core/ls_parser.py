"""
This module contains logic for parsing ls output. It attempts to handle
output when selinux is enabled or disabled and also skip "bad" lines.
"""


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


def parse_non_selinux(links, owner, group, last):
    """
    Parse part of an ls output line that isn't selinux.

    Args:
        link count, owner, group, and everything else.

    Returns:
        A dict containing links, owner, group, date, and name. If the line
        represented a device, major and minor numbers are included.  Otherwise,
        size is included. If the raw name was a symbolic link, link is
        included.
    """
    # prw-------.  1 0 0   0 Jun 28 09:44 5.ref
    # l??????????  ? ? ?    ?            ? invocation:auditd.service

    result = {
        "links": int(links) if links.isdigit() else links,
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
        result["size"] = int(size) if size.isdigit() else size

    # The date part is always 12 characters regardless of content.
    result["date"] = rest[:12]

    # Jump over the date and the following space to get the path part.
    path, link = parse_path(rest[13:])
    result["name"] = path
    if link:
        result["link"] = link

    return result


def parse_selinux(owner, group, selinux_str, name_part):
    """
    Parse part of an ls output line that is selinux.

    Args:
        owner, group, selinux info, and the path.

    Returns:
        A dict containing owner, group, se_user, se_role, se_type, se_mls, and
        name. If the raw name was a symbolic link, link is also included.

    """

    selinux = selinux_str.split(":")
    lsel = len(selinux)
    name, link = parse_path(name_part)
    result = {
        "owner": owner,
        "group": group,
        "se_user": selinux[0],
        "se_role": selinux[1] if lsel > 1 else None,
        "se_type": selinux[2] if lsel > 2 else None,
        "se_mls": selinux[3] if lsel > 3 else None,
        "name": name
    }
    if link:
        result["link"] = link
    return result


def parse_rhel8_selinux(links, owner, group, last):
    """
    Parse part of an ls output line that is selinux on RHEL8.

    Args:
        link count, owner, group, and everything else.

    Returns:
        A dict containing links, owner, group, se_user, se_role, se_type,
        se_mls, size, date, and name. If the raw name was a symbolic link,
        link is also included.

    """
    result = {
        "links": int(links) if links.isdigit() else links,
        "owner": owner,
        "group": group,
    }
    selinux, last = last.split(None, 1)
    selinux = selinux.split(":")
    lsel = len(selinux)
    if "," in last:
        major, minor, last = last.split(None, 2)
        result['major'] = int(major.rstrip(","))
        result['minor'] = int(minor)
    else:
        size, last = last.split(None, 1)
        result['size'] = int(size) if size.isdigit() else size
    date = last[:12]
    path, link = parse_path(last[13:])
    result.update(
        {
            "se_user": selinux[0],
            "se_role": selinux[1] if lsel > 1 else None,
            "se_type": selinux[2] if lsel > 2 else None,
            "se_mls": selinux[3] if lsel > 3 else None,
            "name": path,
            "date": date,
        }
    )
    if link:
        result["link"] = link
    return result


parse_mode = {
    'normal': parse_non_selinux,
    'selinux': parse_selinux,
    'rhel8_selinux': parse_rhel8_selinux
}


class Directory(dict):
    def __init__(self, name, total, body):
        dirs = []
        ents = {}
        files = []
        specials = []
        mode = None
        for line in body:
            # we can't split(None, 5) here b/c rhel 6/7 selinux lines only have
            # 4 parts before the path, and the path itself could contain
            # spaces. Unfortunately, this means we have to split the line again
            # below
            perms, links, owner, group, rest = line.split(None, 4)
            typ = perms[0]
            entry = {
                "type": typ,
                "perms": perms[1:]
            }
            # determine mode once per directory
            if mode is None:
                if links[0].isdigit():
                    # We have to split the line again to see if this is a RHEL8
                    # selinux stanza. This assumes that the context section will
                    # always have at least two pieces separated by ':'.
                    # '?' as the whole RHEL8 security context is also acceptable.
                    rhel8_selinux_ctx = line.split()[4]
                    if ":" in rhel8_selinux_ctx or '?' == rhel8_selinux_ctx.strip():
                        # drwxr-xr-x. 2 root root unconfined_u:object_r:var_lib_t:s0 54 Apr  8 16:41 abcd-efgh-ijkl-mnop
                        mode = 'rhel8_selinux'
                    else:
                        # crw-------.  1 0 0 10,  236 Jul 25 10:00 control
                        # lrwxrwxrwx.  1 0 0       11 Aug  4  2014 menu.lst -> ./grub.conf
                        mode = 'normal'
                else:
                    # -rw-r--r--. root root system_u:object_r:boot_t:s0      config-3.10.0-267
                    mode = 'selinux'
            # Now parse based on mode
            rest = parse_mode[mode](links, owner, group, rest)

            # Update our entry and put it into the correct buckets
            # based on its type.
            entry.update(rest)
            # TODO
            # - The `raw_entry` key is deprecated and will be removed from 3.6.0.
            #   Please use the `insights.parsers.ls.FileListingParser.raw_entry_of` instead.
            entry["raw_entry"] = line
            entry["dir"] = name
            nm = entry["name"]
            ents[nm] = entry
            if typ not in "bcd":
                files.append(nm)
            elif typ == "d":
                dirs.append(nm)
            elif typ in "bc":
                specials.append(nm)

        super(Directory, self).__init__(
            {
                "dirs": dirs,
                "entries": ents,
                "files": files,
                "name": name,
                "specials": specials,
                "total": total,
            }
        )


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
        # Skip empty line and non-exist dir line
        if not line or ': No such file or directory' in line:
            continue
        if line[0] == "/" and line[-1] == ":":
            # Directory name - like '/tmp:'
            if total is None:
                total = len(entries)
            # Some old directory listings don't have an initial name line,
            # so we put any entries we collected before a named directory in
            # our 'root' directory - if we got a 'root' directory at all...
            old_name = root if name is None else name
            if old_name is not None:
                doc[old_name] = Directory(old_name, total, entries)
            name = line[:-1]
            total = None
            entries = []
            continue
        if line.startswith("total"):
            # Should be first line after directory name
            total = int(line[6:])
            continue
        entries.append(line)
    name = name or root
    total = total if total is not None else len(entries)
    doc[name] = Directory(name, total, entries)
    return doc
