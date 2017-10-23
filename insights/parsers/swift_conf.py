"""
SwiftProxyServerConf - file ``/etc/swift/proxy-server.conf``
============================================================

This module provides parsers for swift config files under /etc/swift directory.
"""

from .. import IniConfigFile, parser


@parser("proxy_server.conf")
class SwiftProxyServerConf(IniConfigFile):
    """
    This class is to parse the content of the ``/etc/swift/proxy-server.conf``.

    The swift proxy - server configuration file
    ``/etc/swift/proxy-server.conf`` is in the standard 'ini' format and is
    read by the :py:class:`insights.core.IniConfigFile` parser class.

    Sample configuration file::

        [DEFAULT]
        bind_port = 8080
        bind_ip = 172.20.15.20
        workers = 0
        [pipeline:main]
        pipeline = catch_errors healthcheck proxy-logging cache ratelimit

        [app:proxy-server]
        use = egg:swift  # proxy
        set log_name = proxy-server
        set log_facility = LOG_LOCAL1

        [filter:catch_errors]
        use = egg:swift  # catch_errors

    Examples:
        >>> proxy_server_conf = shared[SwiftProxyServerConf]
        >>> 'app:proxy-server' in proxy_server_conf
        True
        >>> proxy_server_conf.get('filter:catch_errors', 'use')
        'egg:swift#catch_errors'
        >>> proxy_server_conf.getint('DEFAULT', 'bind_port')
        8080
    """
    pass
