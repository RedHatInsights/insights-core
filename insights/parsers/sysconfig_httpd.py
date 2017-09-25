from .. import parser, SysconfigOptions


@parser('sysconfig_httpd')
class HTTPDService(SysconfigOptions):
    """
    .. warning::
        Deprecated parser, please use
        :class:`insights.parsers.sysconfig.HttpdSysconfig` instead.
    """
    pass
