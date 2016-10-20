import os
from collections import OrderedDict

__all__ = [f.split(".")[0] for f in os.listdir(os.path.dirname(__file__)) if f.endswith(".py")]


class ParseException(Exception):
    """
    Exception that should be thrown from mappers that encounter
    exceptions they recognize while parsing.
    """
    pass


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


def split_kv_pairs(lines, comment_char="#", filter_string=None, split_on="=", use_partition=False, ordered=False):
    """Split lines of a list into key/value pairs

    Use this function to filter and split all lines of a list of strings into
    a dictionary. Named arguments may be used to control how the line is split,
    how lines are filtered and the type of output returned.  See parameters for
    more information.  When splitting key/value, the first occurence of the
    split character is used, other occurrences of the split char in the line
    will be ignored. ::func:`get_active_lines` is called to strip comments and
    blank lines from the data.

    Parameters
    ----------
    lines: list of str
        List of the strings to be split.
    comment_char: char default=`#`
        Char that when present in the line indicates all following chars are part
        of a comment.  If this is present, all comments and all blank lines are
        removed from list before further processing.  The default comment char is
        the `#` character.
    filter_string: str
        If the filter string is present, then only lines containing the filter will
        will be processed, other lines will be ignored.
    split_on: char default=`=`
        Character to use when splitting a line.  Only the first occurence of the
        char is used when splitting, so only one split is performed at the first
        occurrence of `split_on`.
    use_partition: boolean default=`False`
        If this parameter is `True` then the python `partition` function will be used
        to split the line. If `False` then the pyton `split` function will be used.
        The difference is that when `False`, if the split character is not present
        in the line then the line is ignored and when `True` the line will be parsed
        regardless.  Set `use_partition` to `True` if you have valid lines that
        do not contain the `split_on` character.  Set `use_partition` to `False`
        if you want to ignore lines that do not contain the `split_on` character.
    ordered: boolean default=`False`
        If this parameter is `True` then the resulting dictionary will be in the
        same order as in the original file, a python `OrderedDict` type is used.
        If this parameter is `False` then the resulting dictionary is in no
        particular order, a base python `dict` type is used.

    Returns
    -------
    dictionary: dict or OrderedDict
        Return value is a dictionary of the key/value pairs.  If parameter `keyword` is `True`
        then an OrderedDict is returned, otherwise a dict is returned.

    Examples
    --------
    >>> from .. import split_kv_pairs
    >>> for line in lines:
    ...     print line
    # Comment line
    # Blank lines will also be removed
    keyword1 = value1   # Inline comments
    keyword2 = value2a=True, value2b=100M
    keyword3     # Key with no separator
    >>> split_kv_pairs(lines)
    {'keyword2': 'value2a=True, value2b=100M', 'keyword1': 'value1'}
    >>> split_kv_pairs(lines, comment_char='#')
    {'keyword2': 'value2a=True, value2b=100M', 'keyword1': 'value1'}
    >>> split_kv_pairs(lines, filter_string='keyword2')
    {'keyword2': 'value2a=True, value2b=100M'}
    >>> split_kv_pairs(lines, use_partition=True)
    {'keyword3': '', 'keyword2': 'value2a=True, value2b=100M', 'keyword1': 'value1'}
    >>> split_kv_pairs(lines, use_partition=True, ordered=True)
    OrderedDict([('keyword1', 'value1'), ('keyword2', 'value2a=True, value2b=100M'), ('keyword3', '')])

    """
    _lines = lines if comment_char is None else get_active_lines(lines, comment_char=comment_char)
    _lines = _lines if filter_string is None else [l for l in _lines if filter_string in l]
    kv_pairs = OrderedDict() if ordered else {}

    for line in _lines:
        if not use_partition:
            if split_on in line:
                k, v = line.split(split_on, 1)
                kv_pairs[k.strip()] = v.strip()
        else:
            k, _, v = line.partition(split_on)
            kv_pairs[k.strip()] = v.strip()
    return kv_pairs
