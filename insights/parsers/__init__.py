import pkgutil
from collections import OrderedDict


__all__ = [n for (i, n, p) in pkgutil.iter_modules(__path__) if not p]


class ParseException(Exception):
    """
    Exception that should be thrown from parsers that encounter
    exceptions they recognize while parsing. When this exception
    is thrown, the exception message and data are logged and no
    parser output data is saved.
    """
    pass


class SkipException(Exception):
    """
    Exception that should be thrown from parsers that are explicitly
    written to look for errors in input data.  If the expected error
    is not found then the parser should throw this exception to
    signal to the infrastructure that the parser's output should not be
    retained.
    """
    pass


def get_active_lines(lines, comment_char="#"):
    """
    Returns lines, or parts of lines, from content that are not commented out
    or completely empty.  The resulting lines are all individually stripped.

    This is useful for parsing many config files such as ifcfg.

    Parameters:
        lines (list): List of strings to parse.
        comment_char (str): String indicating that all chars following
            are part of a comment and will be removed from the output.

    Returns:
        list: List of valid lines remaining in the input.

    Examples:
        >>> lines = [
        ... 'First line',
        ... '   ',
        ... '# Comment line',
        ... 'Inline comment # comment',
        ... '          Whitespace          ',
        ... 'Last line']
        >>> get_active_lines(lines)
        ['First line', 'Inline comment', 'Whitespace', 'Last line']
    """
    return filter(None, (line.split(comment_char, 1)[0].strip() for line in lines))


def optlist_to_dict(optlist, opt_sep=',', kv_sep='='):
    """Parse an option list into a dictionary.

    Takes a list of options separated by ``opt_sep`` and places them into
    a dictionary with the default value of ``True``.  If ``kv_sep`` option
    is specified then key/value options ``key=value`` are parsed.  Useful
    for parsing options such as mount options in the format
    ``rw,ro,rsize=32168,xyz``.

    Parameters:
        optlist (str): String of options to parse.
        opt_sep (str): Separater used to split options.
        kv_sep (str): If not `None` then `optlist` includes key=value pairs
            to be split, and this str is used to split them.

    Returns:
        dict: Returns a dictionary of names present in the list.  If `kv_sep`
        is not `None` then the values will be the str on the right-hand side
        of `kv_sep`.  If `kv_sep` is `None` then each key will have a default
        value of `True`.

    Examples:
        >>> optlist = 'rw,ro,rsize=32168,xyz'
        >>> optlist_to_dict(optlist)
        {'rw': True, 'ro': True, 'rsize': '32168', 'xyz': True}
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

    Parameters:
        lines (list of str): List of the strings to be split.
        comment_char (str): Char that when present in the line indicates all
            following chars are part of a comment.  If this is present, all
            comments and all blank lines are removed from list before further
            processing.  The default comment char is the `#` character.
        filter_string (str): If the filter string is present, then only lines
            containing the filter will be processed, other lines will be ignored.
        split_on (str): Character to use when splitting a line.  Only the first
            occurence of the char is used when splitting, so only one split is
            performed at the first occurrence of `split_on`.  The default string is `=`.
        use_partition (bool): If this parameter is `True` then the python `partition`
            function will be used to split the line. If `False` then the pyton `split`
            function will be used. The difference is that when `False`, if the split
            character is not present in the line then the line is ignored and when
            `True` the line will be parsed regardless. Set `use_partition` to `True`
            if you have valid lines that do not contain the `split_on` character.
            Set `use_partition` to `False` if you want to ignore lines that do not
            contain the `split_on` character. The default value is `False`.
        ordered (bool): If this parameter is `True` then the resulting dictionary
            will be in the same order as in the original file, a python
            `OrderedDict` type is used. If this parameter is `False` then the resulting
            dictionary is in no particular order, a base python `dict` type is used.
            The default is `False`.

    Returns:
        dict: Return value is a dictionary of the key/value pairs.  If parameter
        `keyword` is `True` then an OrderedDict is returned, otherwise a dict
        is returned.

    Examples:
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


def unsplit_lines(lines, cont_char='\\', keep_cont_char=False):
    """Recombine lines having a continuation character at end.

    Generator that recombines lines in the list that have the char `cont_char`
    at the end of a line.  If `cont_char` is found in a line then then
    next line will be appended to the current line, this will continue for
    multiple continuation lines until the next line is found with no
    continuation character at the end.  All lines found will be combined and
    returned.

    If the `keep_cont_char` option is set to True, the continuation character
    will be left on the end of the line.  Otherwise, by default, it is removed.

    Parameters:
        lines (list): List of strings to be evaluated.
        cont_char (char): Char to search for at end of line. Default is ``\\``.
        keep_cont_char (bool): Whether to keep the continuation on the end of
            the line.  Defaults to False, which causes the continuation
            character to be removed.

    Yields:
        line (str): Yields unsplit lines

    Examples:
        >>> lines = ['Line one \\', '     line one part 2', 'Line two']
        >>> list(unsplit_lines(lines))
        ['Line one      line one part 2', 'Line two']
        >>> list(unsplit_lines(lines, cont_char='2'))
        ['Line one \\', '     line one part Line two']
        >>> list(unsplit_lines(lines, keep_cont_char=True)
        ['Line one \     line one part 2', 'Line two']
    """
    unsplit_lines = []
    for line in lines:
        line = line.rstrip()
        if line.endswith(cont_char):
            unsplit_lines.append(line if keep_cont_char else line[:-1])
        else:
            yield ''.join(unsplit_lines) + line
            unsplit_lines = []
    if unsplit_lines:
        yield ''.join(unsplit_lines)


def calc_offset(lines, target, invert_search=False):
    """
    Function to search for a line in a list starting with a target string.
    If `target` is `None` or an empty string then `0` is returned.  This
    allows checking `target` here instead of having to check for an empty
    target in the calling function. Each line is stripped of leading spaces
    prior to comparison with each target however target is not stripped.
    See `parse_fixed_table` in this module for sample usage.

    Arguments:
        lines (list): List of strings.
        target (list): List of strings to search for at the beginning of any
            line in lines.
        invert_search (boolean): If `True` this flag causes the search to continue
            until the first line is found not matching anything in target.
            An empty line is implicitly included in target.  Default is `False`.
            This would typically be used if trimming trailing lines off of a
            file by passing `reversed(lines)` as the `lines` argument.

    Returns:
        int: index into the `lines` indicating the location of `target`. If
        `target` is `None` or an empty string `0` is returned as the offset.
        If `invert_search` is `True` the index returned will point to the line
        after the last target was found.

    Raises:
        ValueError: Exception is raised if `target` string is specified and it
            was not found in the input lines.

    Examples:
        >>> lines = [
        ... '#   ',
        ... 'Warning line',
        ... 'Error line',
        ... '    data 1 line',
        ... '    data 2 line']
        >>> target = ['data']
        >>> calc_offset(lines, target)
        3
        >>> target = ['#', 'Warning', 'Error']
        >>> calc_offset(lines, target, invert_search=True)
        3
    """
    if target and target[0] is not None:
        for offset, line in enumerate(l.strip() for l in lines):
            found_any = any([line.startswith(t) for t in target])
            if not invert_search and found_any:
                return offset
            elif invert_search and not(line == '' or found_any):
                return offset

        # If we get here then we didn't find any of the targets
        raise ValueError("Line containing '{}' was not found in table".format(','.join(target)))
    else:
        # If no target then return index 0
        return 0


def parse_fixed_table(table_lines,
                      heading_ignore=None,
                      header_substitute=None,
                      trailing_ignore=None):
    """
    Function to parse table data containing column headings in the first row and
    data in fixed positions in each remaining row of table data.
    Table columns must not contain spaces within the column name.  Column headings
    are assumed to be left justified and the column data width is the width of the
    heading label plus all whitespace to the right of the label.  This function
    will handle blank columns.

    Arguments:
        table_lines (list): List of strings with the first line containing column
            headings separated by spaces, and the remaining lines containing
            table data in left justified format.
        heading_ignore (list): Optional list of strings to search for at
            beginning of line.  All lines before this line will be ignored.
            If specified then it must be present in the file or `ValueError` will
            be raised.
        header_substitute (list): Optional list of tuples containing
            `(old_string_value, new_string_value)` to be used to modify header
            values.  If whitespace is present in a column it must be replaced with
            non-whitespace characters in order for the table to be parsed correctly.
        trailing_ignore (list): Optional list of strings to look for at the end
            rows of the content.  Lines starting with these strings will be ignored,
            thereby truncating the rows of data.

    Returns:
        list: Returns a list of dict for each row of column data.  Dict keys
            are the column headings in the same case as input.

    Raises:
        ValueError: Raised if `heading_ignore` is specified and not found in `table_lines`.

    Sample input::

        Column1    Column2    Column3
        data1      data 2     data   3
        data4      data5      data6

    Examples:
        >>> table_data = parse_fixed_table(table_lines)
        >>> table_data
        [{'Column1': 'data1', 'Column2': 'data 2', 'Column3': 'data   3'},
         {'Column1': 'data4', 'Column2': 'data5', 'Column3': 'data6'}]
    """
    heading_ignore = heading_ignore if heading_ignore is not None else []
    trailing_ignore = trailing_ignore if trailing_ignore is not None else []

    first_line = calc_offset(table_lines, heading_ignore)
    try:
        last_line = len(table_lines) - calc_offset(reversed(table_lines),
                                                   trailing_ignore,
                                                   invert_search=True)
    except ValueError:
        last_line = len(table_lines)

    header = table_lines[first_line]
    if header_substitute:
        for old_val, new_val in header_substitute:
            header = header.replace(old_val, new_val)
    col_headers = header.strip().split()
    col_index = [header.index(c) for c in col_headers]

    table_data = []
    for line in table_lines[first_line + 1:last_line]:
        col_data = {
            col_headers[c]: line[col_index[c]:col_index[c + 1]].strip()
            for c in range(len(col_index) - 1)
        }
        col_data[col_headers[-1]] = line[col_index[-1]:].strip()
        table_data.append(col_data)

    return table_data


def keyword_search(rows, **kwargs):
    """
    Takes a list of dictionaries and finds all the dictionaries where the
    keys and values match those found in the keyword arguments.

    Arguments:
        rows (list): A list of dictionaries representing the data to be
            searched.
        **kwargs (dict): keyword-value pairs corresponding to the fields that
            need to be found and their required values in the data rows.

    Returns:
        (list): The list of rows that match the search keywords.  If no
            keyword arguments are given, no rows are returned.

    Examples:
        >>> rows = [
        ...     {'domain': 'oracle', 'type': 'soft', 'item': 'nofile', 'value': 1024},
        ...     {'domain': 'oracle', 'type': 'hard', 'item': 'nofile', 'value': 65536},
        ...     {'domain': 'oracle', 'type': 'soft', 'item': 'stack', 'value': 10240},
        ...     {'domain': 'oracle', 'type': 'hard', 'item': 'stack', 'value': 3276},
        ...     {'domain': 'root', 'type': 'soft', 'item': 'nproc', 'value': -1}]
        ...
        >>> keyword_search(rows, domain='root')
        [{'domain': 'root', 'type': 'soft', 'item': 'nproc', 'value': -1}]
    """
    results = []
    if not kwargs:
        return results
    return [
        row for row in rows
        if all([key in row and row[key] == value for key, value in kwargs.iteritems()])
    ]
