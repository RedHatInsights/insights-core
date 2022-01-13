"""
OpenStack gnocchi related files or commands
===========================================

Module for the processing of gnocchi related files and commands.
This module provides parsers:

GnocchiConf - file ``/etc/gnocchi.gnocchi.conf``
------------------------------------------------

GnocchiMetricdLog - file ``gnocchi-metricd.log`` or ``metricd.log``
-------------------------------------------------------------------
"""

from insights.core import IniConfigFile, LogFileOutput
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs


add_filter(Specs.gnocchi_conf, "[")


@parser(Specs.gnocchi_conf)
class GnocchiConf(IniConfigFile):
    """
    Gnocchi configuration parser class, based on the ``IniConfigFile`` class.

    The gnocchi configuration file is a standard '.ini' file and this parser uses
    the ``IniConfigFile`` class to read it.

    Sample configuration::

        [DEFAULT]
        log_dir = /var/log/gnocchi
        [api]
        auth_mode = keystone
        max_limit = 1000
        [archive_policy]
        [indexer]
        url = mysql+pymysql://gnocchi:exampleabckeystring@192.168.0.1/gnocchi?charset=utf8
        [metricd]
        workers = 2
        [oslo_middleware]
        [oslo_policy]
        policy_file = /etc/gnocchi/policy.json
        [statsd]
        resource_id = 5e3fcbe2-7aab-475d-b42c-abcdefgh
        user_id = e0ca4711-1128-422c-abd6-abcdefgh
        project_id = af0c88e8-90d8-4795-9efe-abcdefgh
        archive_policy_name = high
        flush_delay = 10
        [storage]
        driver = file
        file_basepath = /var/lib/gnocchi
        [keystone_authtoken]
        auth_uri=http://192.168.0.1:5000/v3
        auth_type=password
        auth_version=v3
        auth_url=http://192.168.0.1:35357
        username=gnocchi
        password=yourpassword23432
        user_domain_name=Default
        project_name=services
        project_domain_name=Default


    Examples:
        >>> type(conf)
        <class 'insights.parsers.gnocchi.GnocchiConf'>
        >>> sorted(conf.sections()) == sorted([u'api', u'archive_policy', u'indexer', u'metricd', u'oslo_middleware', u'oslo_policy', u'statsd', u'storage', u'keystone_authtoken'])
        True
        >>> 'storage' in conf
        True
        >>> conf.has_option('indexer', 'url')
        True
        >>> conf.get('indexer', 'url') == u'mysql+pymysql://gnocchi:exampleabckeystring@192.168.0.1/gnocchi?charset=utf8'
        True
        >>> conf.getint("statsd", "flush_delay")
        10
    """
    pass


@parser(Specs.gnocchi_metricd_log)
class GnocchiMetricdLog(LogFileOutput):
    """
    Provide access to metricd.log using the LogFileOutput parser class.


    This log file is a standard log parser based on the LogFileOutput class.
    From OpenStack 12, the log ``metricd.log`` is renamed to ``gnocchi-metricd.log``

    Sample log file::

        2017-04-12 03:10:53.076 14550 INFO gnocchi.cli [-] 0 measurements bundles across 0 metrics wait to be processed.
        2017-04-12 03:12:53.078 14550 INFO gnocchi.cli [-] 0 measurements bundles across 0 metrics wait to be processed.
        2017-04-12 03:14:53.080 14550 INFO gnocchi.cli [-] 0 measurements bundles across 0 metrics wait to be processed.
        2017-04-13 21:06:11.676 114807 ERROR tooz.drivers.redis ToozError: Cannot extend an unlocked lock

    Examples:

        >>> 'measurements bundles across 0 metrics wait to be processed' in log
        True
        >>> log.get('ERROR')
        [{'raw_message': '2017-04-13 21:06:11.676 114807 ERROR tooz.drivers.redis ToozError: Cannot extend an unlocked lock'}]
        >>> from datetime import datetime
        >>> list(log.get_after(datetime(2017, 4, 12, 19, 36, 38)))
        [{'raw_message': '2017-04-13 21:06:11.676 114807 ERROR tooz.drivers.redis ToozError: Cannot extend an unlocked lock'}]

    """
    pass
