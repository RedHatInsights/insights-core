"""
openshift configuration files - File
======================================================================================
``/etc/origin/node/node-config.yaml`` and ``/etc/origin/master/master-config.yaml``
are configuration files of openshift Master node and Node node. Their format are both
``yaml``.


Examples:
    >>> result = shared[OseMasterConfig]
    >>> result.data['assetConfig']['masterPublicURL']
    'https://master.ose.com:8443'
    >>> result.data['corsAllowedOrigins'][1]
    'localhost'
"""

from .. import YAMLMapper, mapper


@mapper('ose_node_config')
class OseNodeConfig(YAMLMapper):
    """Class to parse ``/etc/origin/node/node-config.yaml``"""
    pass


@mapper('ose_master_config')
class OseMasterConfig(YAMLMapper):
    """Class to parse ``/etc/origin/master/master-config.yaml``"""
    pass
