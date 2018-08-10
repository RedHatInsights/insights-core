from insights.configtree import LineGetter, PushBack, eat_whitespace, parse_bare


PERMBITS = set("-+.dlbcpsrwxtT")


def parse_name(lg):
    if lg.peek().endswith(":"):
        return next(lg).strip().rstrip(":")


def parse_total(lg):
    if lg.peek().startswith("total"):
        return int(next(lg).split()[1])


def parse_perms(pb):
    perms = []
    while pb.peek() in PERMBITS:
        perms.append(next(pb))

    return {
        "type": perms[0],
        "perms": "".join(perms[1:])
    }


def parse_path(pb):
    eat_whitespace(pb)
    path = "".join(list(pb))
    path, _, link = path.partition(" -> ")
    return path, (link or None)


def parse_non_selinux(pb):
    eat_whitespace(pb)
    owner = parse_bare(pb)

    eat_whitespace(pb)
    group = parse_bare(pb)
    result = {
        "owner": owner,
        "group": group,
    }

    eat_whitespace(pb)
    size = parse_bare(pb)
    if "," in size:
        major = int(size.strip(","))
        eat_whitespace(pb)
        minor = int(parse_bare(pb))
        result["major"] = major
        result["minor"] = minor
    else:
        result["size"] = int(size)

    eat_whitespace(pb)
    month = parse_bare(pb)

    eat_whitespace(pb)
    day = parse_bare(pb)

    eat_whitespace(pb)
    extra = parse_bare(pb)

    fst = " " * (3 - (len(day)))
    snd = " " * (6 - (len(extra)))

    date = "%s%s%s%s%s" % (month, fst, day, snd, extra)
    path, link = parse_path(pb)

    result["date"] = date
    result["name"] = path
    if link:
        result["link"] = link

    return result


def parse_selinux(pb):
    eat_whitespace(pb)
    group = parse_bare(pb)

    eat_whitespace(pb)
    selinux = parse_bare(pb).split(":")

    path, link = parse_path(pb)
    result = {
        "group": group,
        "se_user": selinux[0],
        "se_role": selinux[1] if len(selinux) > 1 else None,
        "se_type": selinux[2] if len(selinux) > 2 else None,
        "se_mls": selinux[3] if len(selinux) > 3 else None,
        "name": path,
    }
    if link:
        result["link"] = link
    return result


def parse_entry(pb):
    entry = parse_perms(pb)

    eat_whitespace(pb)
    word = parse_bare(pb)
    if word[0].isdigit():
        entry.update({
            "links": int(word),
        })
        rest = parse_non_selinux(pb)
    else:
        entry.update({
            "owner": word,
        })
        rest = parse_selinux(pb)
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
                pb = PushBack(next(lg))
                entry = parse_entry(pb)
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
