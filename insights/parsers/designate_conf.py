"""
DesignateConf - file ``/etc/designate/designate.conf``
======================================================
"""
from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

ADDITIONAL_FILTERS = [
    "[",
    "state_path",
    "root_helper",
    "debug",
    "log_dir",
    "www_authenticate_uri",
    "project_name",
    "project_domain_name",
    "driver"
]
add_filter(Specs.designate_conf, ADDITIONAL_FILTERS)


@parser(Specs.designate_conf)
class DesignateConf(IniConfigFile):
    """
    This class provides parsing for the files:
        ``/var/lib/config-data/puppet-generated/designate/etc/designate/designate.conf``
        ``/etc/designate/designate.conf``

    Sample input data is in the format::

        [DEFAULT]
        state_path=/var/lib/designate
        root_helper=sudo designate-rootwrap /etc/designate/rootwrap.conf
        debug=True
        log_dir=/var/log/designate

        [keystone_authtoken]
        www_authenticate_uri=http://localhost:5000
        project_name=service
        project_domain_name=Default

        [oslo_messaging_notifications]
        driver=messagingv2

    Examples:
        >>> type(conf)
        <class 'insights.parsers.designate_conf.DesignateConf'>
        >>> conf.sections()
        ['keystone_authtoken', 'oslo_messaging_notifications']
        >>> conf.has_option('DEFAULT', 'debug')
        True
        >>> conf.get("oslo_messaging_notifications", "driver")
        'messagingv2'
    """
    pass
