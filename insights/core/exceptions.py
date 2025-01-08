"""
Exceptions
==========
"""

from insights.parsr.iniparser import NoOptionError, NoSectionError  # noqa: F401


class BlacklistedSpec(Exception):
    """
    Exception to be thrown when a blacklisted spec is found.
    """

    pass


class CalledProcessError(Exception):
    """
    Raised if call fails.

    Parameters:
        returncode (int): The return code of the process executing the command.
        cmd (str): The command that was executed.
        output (str): Any output the command produced.
    """

    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        super(CalledProcessError, self).__init__(returncode, cmd, output)

    def __unicode__(self):
        name = self.__class__.__name__
        rc = self.returncode
        cmd = self.cmd
        output = self.output
        return '<{}({}, {!r}, {!r})>'.format(name, rc, cmd, output)


class InvalidArchive(Exception):
    """
    Raised when archive cannot be identified or missing expected structure.
    """

    def __init__(self, msg):
        super(InvalidArchive, self).__init__(msg)
        self.msg = msg


class InvalidContentType(InvalidArchive):
    """
    Raised when invalid content_type is specified.
    """

    def __init__(self, content_type):
        msg = 'Invalid content type: "%s"' % content_type
        super(InvalidContentType, self).__init__(msg)
        self.msg = msg
        self.content_type = content_type


class MissingRequirements(Exception):
    """
    Raised during evaluation if a component's dependencies aren't met.
    """

    def __init__(self, requirements):
        self.requirements = requirements
        super(MissingRequirements, self).__init__(requirements)


class NoFilterException(Exception):
    """
    Raised whenever no filters added to a `filterable` :class:`datasource`.
    """

    pass


class ParseException(Exception):
    """
    Exception that should be thrown from parsers that encounter
    exceptions they recognize while parsing. When this exception
    is thrown, the exception message and data are logged and no
    parser output data is saved.
    """

    pass


class SkipComponent(Exception):
    """
    This class should be raised by components that want to be taken out of
    dependency resolution.
    """

    pass


class ContentException(SkipComponent):
    """
    Raised whenever a :class:`datasource` fails to get data.
    """

    pass


class TimeoutException(Exception):
    """
    Raised whenever a :class:`datasource` hits the set timeout value.
    """

    pass


class ValidationException(Exception):
    """
    Raised when passes invalid arguments to Response.
    """

    def __init__(self, msg, r=None):
        if r:
            msg = "%s: %s" % (msg, r)
        super(ValidationException, self).__init__(msg)
