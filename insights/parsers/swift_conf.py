"""
Swift Conf Files - file ``/etc/swift/``
=======================================

This module provides parsers for swift config files under /etc/swift directory.

SwiftObjectExpirerConf - file ``/etc/swift/object-expirer.conf``
----------------------------------------------------------------

SwiftProxyServerConf - file ``/etc/swift/proxy-server.conf``
------------------------------------------------------------
"""

from .. import IniConfigFile, parser
from ..specs import Specs


@parser(Specs.swift_proxy_server_conf)
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


@parser(Specs.swift_object_expirer_conf)
class SwiftObjectExpirerConf(IniConfigFile):
    """
    This class is to parse the content of the ``/etc/swift/object-expirer.conf``.

    `/etc/swift/object-expirer.conf`` is in the standard 'ini' format and is
    read by the :py:class:`insights.core.IniConfigFile` parser class.

    Sample configuration file::

        [DEFAULT]

        [object-expirer]
        # auto_create_account_prefix = .
        auto_create_account_prefix = .
        process=0
        concurrency=1
        recon_cache_path=/var/cache/swift
        interval=300
        reclaim_age=604800
        report_interval=300
        processes=0
        expiring_objects_account_name=expiring_objects

        [pipeline:main]
        pipeline = catch_errors cache proxy-server

        [app:proxy-server]
        use = egg:swift#proxy

        [filter:cache]
        use = egg:swift#memcache
        memcache_servers = 172.16.64.60:11211

        [filter:catch_errors]
        use = egg:swift#catch_errors

    Examples:
        >>> object_expirer_conf = shared[SwiftObjectExpirerConf]
        >>> 'filter:cache' in proxy_server_conf
        True
        >>> proxy_server_conf.get('filter:cache', 'memcache_servers')
        '172.16.64.60:11211'
        >>> proxy_server_conf.getint('object-expirer', 'report_interval')
        300
    """
    pass
