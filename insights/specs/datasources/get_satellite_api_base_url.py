"""
Custom datasources for get satellite version on satellite client.
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.rhsm_conf import RHSMConf


@datasource(HostContext, RHSMConf)
def base_url_of_satellite_api(broker):
    """
    Get the base url of satellite API on satellite client.

    Returns:
        string: base url to call the satelltie API on satellite client.

    Raises:
        SkipComponent: When the host is registered to the public cdn.
    """
    rhsm_conf = broker.get(RHSMConf)
    cdn_hosts = ['subscription.rhsm.redhat.com', 'subscription.rhn.redhat.com']
    # satellite client
    if rhsm_conf and ('server' in rhsm_conf and
        rhsm_conf.has_option('server', 'hostname') and
        rhsm_conf.get('server', 'hostname') not in cdn_hosts and
            rhsm_conf.has_option('server', 'port')):
        return 'https://%s:%s' % (
            str(rhsm_conf.get('server', 'hostname')),
            str(rhsm_conf.get('server', 'port')))
    raise SkipComponent()
