import os
from functools import reduce


def path_join(path1, path2):
    # os.path.join drops path1 entirely if path2 starts with a '/' which makes sense
    #    in some circomstances, but almost never in this program
    # so we use path_join instead
    return os.path.join(path1, path2 if not path2.startswith('/') else path2.lstrip('/'))


def sh_join(split_command):
    # is the reverse of shlex.split
    #   such that for some shell command string X:
    #     shlex.split(sh_join(shlex.split(X))) == shlex.split(X)
    # The point is that you can parse a command string with shlex.split,
    #   manipulate the individual arguments in the resulting array
    #   and then join the individual arguments back together in a way that a future
    #   shlex.split will properly parse the shell command string.
    # Most of the real work happens in sh_quote

    return reduce(lambda accum, arg: accum + ' ' + sh_quote(arg), split_command)


def sh_quote(arg):
    """
    will do shell style quoting for a single shell argument
      such that it can be recombined back into a single string (rather than an array of strings)
      such that shlex.split would resplit the string back into the same array.
    The characters that need quoting within an argument are: double-quote, single-quote, backslash,
      and all the whitespace characters (blank, newline, tab)
    If an arg has none of these, this function returns it as is.
    The simplest implementation of this function would simply put a backslash in front of
      any character that needs special quoting, but that would look really ugly in some cases,
      and since these modified commands end up in the uploader.json file, we try for something
      prettier.
    For the unix shell,
       single-quotes around, quotes everything, but can not contain a quote (this is different
         than Python string literals).
       double-quotes around, quotes single-quotes and whitespace, but double-quotes and backslashes
         must be escaped with a backslash.
       outside of quotes, backslash always escapes the following character

    The way we do this is to count the characters that need quoteing, and ....
    This is simpler to understand, but does at least 6 passes over the string, and can do many
      more.  This generally isn't a problem because most arguments are very short.
    A faster way to implement this would be to do one pass over the string, start building an
      output string as soon as it becomes needed, and stoping once an output string can't be used.
      If more than possible output string is left at the end, choose the best.
      For example, until you see a special character, only the unmodified output string is needed
      As soon as a space is encountered, create the single-quote output, double-quote output,
        and backslash output strings, and drop the unmodified output string.
      As soon as a single-quote is found drop the single-quote output string.
      Etc.

    But for now, do it the slower, simple way.
    """
    double_count = arg.count('"')
    single_count = arg.count("'")
    space_count = arg.count(' ') + arg.count('\t') + arg.count('\n')
    backslash_count = arg.count('\\')

    # To try to make the output as pretty as we can we use the following:
    # if no characters need quoteing, return arg as is
    if double_count + single_count + space_count + backslash_count == 0:
        return arg

    # elif arg contains no single-quotes, return single-quotes around arg
    elif single_count == 0:
        return sh_single_quote(arg)

    # elif we need to quote only 1 or 2 character, use backslashes in front of
    elif double_count + single_count + space_count + backslash_count < 3:
        return sh_backslash_quote(arg)

    # else use double-quotes around
    else:
        return sh_double_quote(arg)


def sh_single_quote(arg):
    # put single-quotes around
    #    this will fail to quote correctly if arg contains any single-quotes
    return "'" + arg + "'"


def sh_double_quote(arg):
    # put double-quotes around, and escape any double-quotes and backslashes within arg
    #   this will always quote correctly
    return '"' + arg.replace('\\', '\\\\').replace('"', '\\"') + '"'


def sh_backslash_quote(arg):
    # quote each special character individually by putting a backslash in front of it.
    #   this will always quote correctly, but is ugly unless only a few characters need quoteing
    # Note that when doing the replaceing, replace the backslashes first or this will fail!
    return arg.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace(' ', '\\ ').replace('\t', '\\\t').replace('\n', '\\\n')
