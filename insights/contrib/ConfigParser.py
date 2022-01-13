from insights.parsr.iniparser import NoOptionError as NOE, NoSectionError as NSE


class NoOptionError(NOE):
    """
    These classes are just here for backwards compatibility
    until other projects can be updated to reference the new
    location of the exceptions in iniparser.
    """
    pass


class NoSectionError(NSE):
    pass
