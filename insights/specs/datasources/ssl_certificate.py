"""
Custom datasource to get ssl certificate file path.
"""
from insights.combiners.httpd_conf import HttpdConfTree
from insights.combiners.nginx_conf import NginxConfTree
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.mssql_conf import MsSQLConf
from insights.combiners.rsyslog_confs import RsyslogAllConf


@datasource(HttpdConfTree, HostContext)
def httpd_certificate_info_in_nss(broker):
    """
    Get the certificate info configured in nss database

    Arguments:
        broker: the broker object for the current session

    Returns:
        list: Returns a list of tuple with the Nss database path and the certificate nickname

    Raises:
        SkipComponent: Raised when NSSEngine isn't enabled or "NSSCertificateDatabase" and
            "NSSNickname" directives aren't found
    """
    conf = broker[HttpdConfTree]
    path_pairs = []
    virtual_hosts = conf.find('VirtualHost')
    for host in virtual_hosts:
        nss_engine = nss_database = cert_name = None
        nss_engine = host.select('NSSEngine')
        nss_database = host.select('NSSCertificateDatabase')
        cert_name = host.select('NSSNickname')
        if nss_engine and nss_engine.value and nss_database and cert_name:
            path_pairs.append((nss_database[0].value, cert_name[0].value))
    if path_pairs:
        return path_pairs
    raise SkipComponent


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
    virtual_hosts = conf.find('VirtualHost')
    ssl_certs = []
    for host in virtual_hosts:
        ssl_cert = ssl_engine = None
        ssl_engine = host.select('SSLEngine')
        ssl_cert = host.select('SSLCertificateFile')
        if ssl_engine and ssl_engine.value and ssl_cert:
            ssl_certs.append(str(ssl_cert.value))
    if ssl_certs:
        return ssl_certs
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


@datasource(RsyslogAllConf, HostContext)
def rsyslog_tls_cert_file(broker):
    """
    Get the rsyslog tls certificate file path configured by "DefaultNetstreamDriverCertFile"

    Arguments:
        broker: the broker object for the current session
    Returns:
        str: Returns the SSL certificate file path configured by "DefaultNetstreamDriverCertFile"
    Raises:
        SkipComponent: Raised if "DefaultNetstreamDriverCertFile" isn't found
    """
    rsyslog_objs = broker[RsyslogAllConf]
    for obj in rsyslog_objs.values():
        for item in obj:
            if 'DefaultNetstreamDriverCertFile' in item:
                if '$DefaultNetstreamDriverCertFile' in item:
                    # basic format
                    return item.split()[-1].strip()
                else:
                    # advanced format
                    # it is set in global block, and the global line contains all the content in it
                    parts = item.split()
                    for part in parts:
                        if 'DefaultNetstreamDriverCertFile' in part:
                            return part.split('=')[-1].strip('"')
    raise SkipComponent
