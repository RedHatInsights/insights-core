"""
Custom datasource to get ssl certificate file path.
"""

from insights.combiners.httpd_conf import HttpdConfTree
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource


@datasource(HttpdConfTree, HostContext)
def httpd_ssl_certificate_file(broker):
    """
    Get the httpd SSL certificate file path configured by "SSLCertificateFile"

    Arguments:
        broker: the broker object for the current session

    Returns:
        str: Returns the SSL certificate file path configured by "SSLCertificateFile"

    Raises:
        SkipComponent: Raised if "SSLCertificateFile" directive isn't found
    """
    conf = broker[HttpdConfTree]
    ssl_cert = conf.find('SSLCertificateFile')
    if ssl_cert and ssl_cert[0].value:
        return str(ssl_cert[0].value)
    raise SkipComponent
