"""
Manila configuration - file ``/etc/manila/manila.conf``
=======================================================

The Manila configuration file is a standard '.ini' file and this parser uses
the ``IniConfigFile`` class to read it.

Sample configuration::

    [DEFAULT]
    osapi_max_limit = 1000
    osapi_share_base_URL = <None>

    use_forwarded_for = false
    api_paste_config = api-paste.ini
    state_path = /var/lib/manila

    scheduler_topic = manila-scheduler

    share_topic = manila-share

    share_driver = manila.share.drivers.generic.GenericShareDriver

    enable_v1_api = false
    enable_v2_api = false

    [cors]
    allowed_origin = <None>
    allow_credentials = true

    expose_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma
    allow_methods = GET,POST,PUT,DELETE,OPTIONS
    allow_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma

Examples:

    >>> conf = shared[ManilaConf]
    >>> conf.sections()
    ['DEFAULT', 'cors']
    >>> 'cors' in conf
    True
    >>> conf.has_option('DEFAULT', 'share_topic')
    True
    >>> conf.get("DEFAULT", "share_topic")
    "manila-share"
    >>> conf.get("DEFAULT", "enable_v2_api")
    "false"
    >>> conf.getboolean("DEFAULT", "enable_v2_api")
    False
    >>> conf.getint("DEFAULT", "osapi_max_limit")
    1000

"""

from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.manila_conf)
class ManilaConf(IniConfigFile):
    """
    Manila configuration parser class, based on the ``IniConfigFile`` class.
    """
    pass
