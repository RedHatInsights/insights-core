from insights.util import deprecated


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
    def __init__(self, msg):
        super(InvalidArchive, self).__init__(msg)
        self.msg = msg


class MissingRequirements(Exception):
    """
    Raised during evaluation if a component's dependencies aren't met.
    """
    def __init__(self, requirements):
        self.requirements = requirements
        super(MissingRequirements, self).__init__(requirements)


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


class TimeoutException(Exception):
    """ Raised whenever a :class:`datasource` hits the set timeout value. """
    pass


class ValidationException(Exception):
    def __init__(self, msg, r=None):
        if r:
            msg = "%s: %s" % (msg, r)
        super(ValidationException, self).__init__(msg)


class ContentException(SkipComponent):
    """ Raised whenever a :class:`datasource` fails to get data. """
    pass


class InvalidContentType(InvalidArchive):
    def __init__(self, content_type):
        self.msg = 'Invalid content type: "%s"' % content_type
        super(InvalidContentType, self).__init__(self.msg)
        self.content_type = content_type


class SkipException(SkipComponent):
    """
    .. warning::
        This class is deprecated, please use
        :py:class:`insights.core.exceptions.SkipComponent` instead.

    Exception that should be thrown from parsers that are explicitly
    written to look for errors in input data.  If the expected error
    is not found then the parser should throw this exception to
    signal to the infrastructure that the parser's output should not be
    retained.
    """
    def __init__(self, msg):
        deprecated(
            SkipException,
            "Please use the :class:`insights.core.exceptions.SkipComponent` instead.",
            "3.3.0"
        )
        super(SkipException, self).__init__(msg)
