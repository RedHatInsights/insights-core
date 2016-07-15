def get_active_lines(lines, comment_char="#"):
    """
    Returns lines, or parts of lines, from content that are not commented out
    or completely empty.

    This is useful for parsing many config files such as ifcfg.
    """
    return filter(None, (line.split(comment_char, 1)[0].strip() for line in lines))
