"""
Cinder configuration - file ``/etc/cinder/cinder.conf``
=======================================================

The Cinder configuration file is a standard '.ini' file and this parser uses
the ``IniConfigFile`` class to read it.

Sample configuration::

    [DEFAULT]
    rpc_backend=cinder.openstack.common.rpc.impl_kombu
    control_exchange=openstack

    osapi_volume_listen=10.22.100.58
    osapi_volume_workers=32

    api_paste_config=/etc/cinder/api-paste.ini
    glance_api_servers=http://10.22.120.50:9292
    glance_api_version=2
    glance_num_retries=0
    glance_api_insecure=False
    glance_api_ssl_compression=False

    enable_v1_api=True
    enable_v2_api=True
    storage_availability_zone=nova
    default_availability_zone=nova
    enabled_backends=tripleo_ceph
    nova_catalog_info=compute:Compute Service:publicURL
    nova_catalog_admin_info=compute:Compute Service:adminURL

    [lvm]
    iscsi_helper=lioadm
    volume_group=cinder-volumes
    iscsi_ip_address=192.168.88.10
    volume_driver=cinder.volume.drivers.lvm.LVMVolumeDriver
    volumes_dir=/var/lib/cinder/volumes
    iscsi_protocol=iscsi
    volume_backend_name=lvm

Examples:

    >>> conf = shared[CinderConf]
    >>> conf.sections()
    ['DEFAULT', 'lvm']
    >>> 'lvm' in conf
    True
    >>> conf.has_option('DEFAULT', 'enabled_backends')
    True
    >>> conf.get("DEFAULT", "enabled_backends")
    "tripleo_ceph"
    >>> conf.get("DEFAULT", "glance_api_ssl_compression")
    "False"
    >>> conf.getboolean("DEFAULT", "glance_api_ssl_compression")
    False
    >>> conf.getint("DEFAULT", "glance_aip_version")
    2

"""

from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.cinder_conf)
class CinderConf(IniConfigFile):
    """
    Cinder configuration parser class, based on the ``IniConfigFile`` class.
    """
    pass
