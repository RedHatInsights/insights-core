from insights.configtree import LineGetter


PERMBITS = set("-+.dlbcpsrwxtT")


def parse_name(lg):
    if lg.peek().endswith(":"):
        return next(lg).strip().rstrip(":")


def parse_total(lg):
    if lg.peek().startswith("total"):
        return int(next(lg).split()[1])


def parse_perms(perms):
    return {
        "type": perms[0],
        "perms": perms[1:]
    }


def parse_path(path):
    path, _, link = path.partition(" -> ")
    return path, (link or None)


def parse_non_selinux(parts):
    links, owner, group = parts[:3]
    result = {
        "links": int(links),
        "owner": owner,
        "group": group,
    }

    size = parts[3]
    start = 4
    if "," in size:
        major = int(size.strip(","))
        minor = int(parts[4])
        start = 5
        result["major"] = major
        result["minor"] = minor
    else:
        result["size"] = int(size)

    month, day, extra = parts[start:start + 3]
    fst = " " * (3 - (len(day)))
    snd = " " * (6 - (len(extra)))
    start += 3

    date = "%s%s%s%s%s" % (month, fst, day, snd, extra)
    path, link = parse_path(" ".join(parts[start:]))

    result["date"] = date
    result["name"] = path
    if link:
        result["link"] = link

    return result


def parse_selinux(parts):
    owner, group = parts[:2]
    selinux = parts[2].split(":")
    path, link = parse_path(" ".join(parts[3:]))
    result = {
        "owner": owner,
        "group": group,
        "se_user": selinux[0],
        "se_role": selinux[1] if len(selinux) > 1 else None,
        "se_type": selinux[2] if len(selinux) > 2 else None,
        "se_mls": selinux[3] if len(selinux) > 3 else None,
        "name": path
    }
    if link:
        result["link"] = link
    return result


def parse_entry(line):
    parts = line.split()
    entry = parse_perms(parts[0])

    if parts[1][0].isdigit():
        rest = parse_non_selinux(parts[1:])
    else:
        rest = parse_selinux(parts[1:])
    entry.update(rest)
    return entry


def parse_stanza(lg, root):
    name = parse_name(lg)
    total = parse_total(lg)
    dirs = []
    ents = {}
    files = []
    specials = []
    while True:
        try:
            line = lg.peek()
            perms = set(line[:10])
            if perms & PERMBITS == perms:
                entry = parse_entry(line)
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
                next(lg)
            else:
                break
        except StopIteration:
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

    return result["name"], result


def parse(lines, root):
    results = {}
    lg = LineGetter(lines)
    while True:
        try:
            line = lg.peek()
            if line.endswith(":") or line.startswith("total"):
                name, stanza = parse_stanza(lg, root)
                results[name] = stanza
            else:
                perms = set(line[:10])
                if perms and perms & PERMBITS == perms:
                    name, stanza = parse_stanza(lg, root)
                    results[name] = stanza
                else:
                    next(lg)
        except StopIteration:
            break
        except:
            try:
                line = next(lg)
            except StopIteration:
                break

    return results
