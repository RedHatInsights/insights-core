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
    lines = iter(lines)
    results = {}
    while True:
        try:
            line = next(lines)
            while not(line):
                line = next(lines)
            try:
                name = None
                total = None
                if line.endswith(":"):
                    name = line[:-1]
                    line = next(lines).strip()
                if line.startswith("total"):
                    total = int(line.split()[1])
                    line = next(lines).strip()

                if not name and not total:
                    continue

                name = name or root
                dirs = []
                ents = {}
                files = []
                specials = []
                while line and line[0] in PERMBITS:
                    parts = line.split(None, 4)
                    perms = parts[0]
                    if len(perms) < 10:
                        line = next(lines).strip()
                        continue
                    typ = perms[0]
                    entry = {
                        "type": typ,
                        "perms": perms[1:]
                    }

                    if parts[1][0].isdigit():
                        rest = parse_non_selinux(parts[1:])
                    else:
                        rest = parse_selinux(parts[1:])
                    entry.update(rest)
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
                    try:
                        line = next(lines).strip()
                    except StopIteration:
                        break

                if total is None:
                    total = len(ents)

                result = {
                    "name": name,
                    "total": total,
                    "entries": ents,
                    "files": files,
                    "dirs": dirs,
                    "specials": specials
                }
                results[result["name"]] = result
            except StopIteration:
                raise
            except Exception:
                line = next(lines)
                log.info("Failed to parse: %s" % line)
        except StopIteration:
            break
    return results
