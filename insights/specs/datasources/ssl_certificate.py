"""
Custom datasource to get ssl certificate file path.
"""

from insights.combiners.nginx_conf import NginxConfTree
from insights.combiners.rsyslog_confs import RsyslogAllConf
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.mssql_conf import MsSQLConf
from insights.specs.datasources import httpd


@datasource(httpd.httpd_configuration_files, HostContext)
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
    confs = broker[httpd.httpd_configuration_files]
    path_pairs = []
    nss_engine = nss_database = cert_name = None
    virtual_host_start = False
    for conf in confs:
        with open(conf) as a_f:
            for line in a_f.readlines():
                line = line.strip()
                if line.startswith('<VirtualHost'):
                    virtual_host_start = True
                    continue
                if virtual_host_start:
                    if line.startswith('NSSEngine'):
                        nss_engine = line.split()[-1].lower().strip('"\'')
                    elif line.startswith('NSSCertificateDatabase'):
                        nss_database = line.split()[-1].lower().strip('"\'')
                    elif line.startswith('NSSNickname'):
                        cert_name = line.split()[-1].lower().strip('"\'')
                    elif line.startswith('</VirtualHost>'):
                        if nss_engine == 'on' and nss_database and cert_name:
                            path_pairs.append((nss_database, cert_name))
                        virtual_host_start = False
                        nss_engine = nss_database = cert_name = None
    if path_pairs:
        return path_pairs
    raise SkipComponent


@datasource(httpd.httpd_configuration_files, HostContext)
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
    confs = broker[httpd.httpd_configuration_files]
    ssl_engine = ssl_cert = None
    ssl_certs = set()
    virtual_host_start = False
    for conf in confs:
        with open(conf) as a_f:
            for line in a_f.readlines():
                line = line.strip()
                if line.startswith('<VirtualHost'):
                    virtual_host_start = True
                    continue
                if virtual_host_start:
                    if line.startswith('SSLEngine'):
                        ssl_engine = line.split()[-1].lower().strip('"\'')
                    elif line.startswith('SSLCertificateFile'):
                        ssl_cert = line.strip().split()[-1].strip('"\'')
                    elif line.startswith('</VirtualHost>'):
                        if ssl_engine == 'on' and ssl_cert:
                            ssl_certs.add(ssl_cert)
                        virtual_host_start = False
                        ssl_engine = ssl_cert = None
    if ssl_certs:
        return sorted(ssl_certs)
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


@datasource(RsyslogAllConf, HostContext)
def rsyslog_tls_ca_cert_file(broker):
    """
    Get the rsyslog tls ca certificate file path configured by "DefaultNetstreamDriverCAFile"

    Arguments:
        broker: the broker object for the current session
    Returns:
        str: Returns the SSL certificate file path configured by "DefaultNetstreamDriverCAFile"
    Raises:
        SkipComponent: Raised if "DefaultNetstreamDriverCAFile" isn't found
    """
    rsyslog_objs = broker[RsyslogAllConf]
    for obj in rsyslog_objs.values():
        for item in obj:
            if 'DefaultNetstreamDriverCAFile' in item:
                if '$DefaultNetstreamDriverCAFile' in item:
                    # basic format
                    return item.split()[-1].strip()
                else:
                    # advanced format
                    # it is set in global block, and the global line contains all the content in it
                    parts = item.split()
                    for part in parts:
                        if 'DefaultNetstreamDriverCAFile' in part:
                            # example: global(DefaultNetstreamDriverCAFile="file_path" test="abc")
                            if '=' in part:
                                return part.split('=')[-1].strip('")')
                            else:
                                # example: global( DefaultNetstreamDriverCAFile = "file_path" test = "abc")
                                name_index = parts.index(part)
                                if len(parts) > name_index + 2:
                                    if parts[name_index + 1].strip() == '=':
                                        path = parts[name_index + 2].strip('")')
                                        if path:
                                            return path
                                # no need to continue
                                raise SkipComponent
    raise SkipComponent
