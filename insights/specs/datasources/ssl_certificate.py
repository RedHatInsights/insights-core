"""
Custom datasource to get ssl certificate file path.
"""

from insights.combiners.httpd_conf import HttpdConfTree
from insights.combiners.nginx_conf import NginxConfTree
from insights.parsers.mssql_conf import MsSQLConf
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource


@datasource(HttpdConfTree, HostContext)
def httpd_ssl_certificate_files(broker):
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
    ssl_certs = conf.find('SSLCertificateFile')
    if ssl_certs:
        return [str(ssl_cert.value) for ssl_cert in ssl_certs]
    raise SkipComponent


@datasource(NginxConfTree, HostContext)
def nginx_ssl_certificate_files(broker):
    """
    Get the nginx SSL certificate file path configured by "ssl_certificate"

    Arguments:
        broker: the broker object for the current session

    Returns:
        str: Returns the SSL certificate file path configured by "ssl_certificate"

    Raises:
        SkipComponent: Raised if "ssl_certificate" directive isn't found
    """
    conf = broker[NginxConfTree]
    ssl_certs = conf.find('ssl_certificate')
    if ssl_certs:
        return [str(ssl_cert.value) for ssl_cert in ssl_certs]
    raise SkipComponent


@datasource(MsSQLConf, HostContext)
def mssql_tls_cert_file(broker):
    """
    Get the mssql tls certificate file path configured by "ssl_certificate"
    Arguments:
        broker: the broker object for the current session
    Returns:
        str: Returns the SSL certificate file path configured by "ssl_certificate"
    Raises:
        SkipComponent: Raised if "ssl_certificate" directive isn't found
    """
    mssql_conf_content = broker[MsSQLConf]
    if mssql_conf_content.has_option("network", "tlscert"):
        return mssql_conf_content.get("network", "tlscert")
    raise SkipComponent
