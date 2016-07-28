import os

__all__ = [f.split(".")[0] for f in os.listdir(os.path.dirname(__file__)) if f.endswith(".py")]


def get_active_lines(lines, comment_char="#"):
    """
    Returns lines, or parts of lines, from content that are not commented out
    or completely empty.  The resulting lines are all individually stripped.

    This is useful for parsing many config files such as ifcfg.
    """
    return filter(None, (line.split(comment_char, 1)[0].strip() for line in lines))


def optlist_to_dict(optlist, opt_sep=',', kv_sep='='):
    """Parse an option list into a dictionary.

    Takes a list of options separated by ``opt_sep`` and places them into
    a dictionary with the default value of ``True``.  If ``kv_sep`` option
    is specified then key/value options ``key=value`` are parsed.  Useful
    for parsing options such as mount options in the format
    ``rw,ro,rsize=32168,xyz``.
    """
    if kv_sep is not None:
        optdict = {opt: True for opt in optlist.split(opt_sep) if kv_sep not in opt}
        optdict.update({opt.split(kv_sep)[0]: opt.split(kv_sep)[1] for opt in optlist.split(opt_sep) if kv_sep in opt})
    else:
        optdict = {opt: True for opt in optlist.split(opt_sep)}
    return optdict
