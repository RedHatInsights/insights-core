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


class SkipException(SkipComponent):
    """
    Exception that should be thrown from parsers that are explicitly
    written to look for errors in input data.  If the expected error
    is not found then the parser should throw this exception to
    signal to the infrastructure that the parser's output should not be
    retained.
    """
    pass
