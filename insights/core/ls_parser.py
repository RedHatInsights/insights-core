import logging

log = logging.getLogger(__name__)
PERMBITS = set("-+.dlbcpsrwxtT")


def parse_path(path):
    path, _, link = path.partition(" -> ")
    return path, link


def parse_non_selinux(parts):
    links, owner, group, last = parts
    result = {
        "links": int(links),
        "owner": owner,
        "group": group,
    }

    # device numbers only go to 256
    if "," in last[:4]:
        major, minor, rest = last.split(None, 2)
        result["major"] = int(major.rstrip(","))
        result["minor"] = int(minor)
    else:
        size, rest = last.split(None, 1)
        result["size"] = int(size)

    path, link = parse_path(rest[13:])

    result["date"] = rest[:12]
    result["name"] = path
    if link:
        result["link"] = link

    return result


def parse_selinux(parts):
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


def parse(lines, root):
    results = {}
    idx = 0
    length = len(lines)
    while True:
        while idx < length and not lines[idx]:
            idx += 1
        if idx == length:
            break
        line = lines[idx]
        try:
            name = None
            total = None
            if line.endswith(":"):
                name = line[:-1]
                idx += 1
                line = lines[idx]
            if line.startswith("total"):
                total = int(line.split()[1])
                idx += 1
                line = lines[idx]

            dirs = []
            ents = {}
            files = []
            specials = []
            perms = set(line[:10])
            while line and perms & PERMBITS == perms:
                parts = line.split(None, 4)
                entry = {
                    "type": parts[0][0],
                    "perms": parts[0][1:]
                }

                if parts[1][0].isdigit():
                    rest = parse_non_selinux(parts[1:])
                else:
                    rest = parse_selinux(parts[1:])
                entry.update(rest)
                entry["raw_entry"] = line
                entry["dir"] = name or root
                nm = entry["name"]
                ents[nm] = entry
                typ = entry["type"]
                if typ in "bc":
                    specials.append(nm)
                elif typ == "d":
                    dirs.append(nm)
                else:
                    files.append(nm)
                idx += 1
                if idx < length:
                    line = lines[idx]
                    perms = set(line[:10])
                else:
                    break
            total = total if total is not None else len(ents)

            result = {
                "name": name or root,
                "total": total,
                "entries": ents,
                "files": files,
                "dirs": dirs,
                "specials": specials
            }
            results[result["name"]] = result
        except:
            log.info("Failed to parse: %s" % line)
    return results
