"""
HeatConf - file ``/etc/heat/heat.conf``
=======================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.heat_conf)
class HeatConf(IniConfigFile):
    """
    This module provides plugins access to the heat.conf information.

    Typical content of the ``heat.conf`` is::

        [DEFAULT]
        heat_metadata_server_url = http://172.16.0.11:8000
        heat_waitcondition_server_url = http://172.16.0.11:8000/v1/waitcondition
        heat_watch_server_url =http://172.16.0.11:8003
        stack_user_domain_name = heat_stack
        stack_domain_admin = heat_stack_domain_admin
        stack_domain_admin_password = *********
        auth_encryption_key = V48p9fRZzWSRgjE96e2I1oGwn216xgqf
        log_dir = /var/log/heat
        notification_driver=messaging

        [clients_keystone]
        auth_uri =http://192.0.2.18:35357

    Usage of this parser is similar to others that use the ``IniConfigFile`` base
    class.

    Examples:
        >>> type(conf)
        <class 'insights.parsers.heat_conf.HeatConf'>
        >>> 'DEFAULT' in conf
        True
        >>> conf.get('clients_keystone', 'auth_uri')
        'http://192.0.2.18:35357'
    """
    pass
