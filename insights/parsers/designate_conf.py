"""
DesignateConf - file ``/etc/designate/designate.conf``
======================================================

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

See the ``IniConfigFile`` class for examples.
"""
from .. import IniConfigFile, parser, add_filter
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
    """Class to parse file ``designate.conf``."""
    pass
