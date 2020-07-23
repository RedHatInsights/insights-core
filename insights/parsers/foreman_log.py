"""
Foreman and Candlepin logs
==========================

Module for parsing the log files in foreman-debug archive

.. note::
    Please refer to its super-class :class:`insights.core.LogFileOutput` for
    usage information.

Parsers provided by this module:

CandlepinErrorLog - file ``sos_commands/foreman/foreman-debug/var/log/candlepin/error.log``
-------------------------------------------------------------------------------------------

CandlepinLog - file ``/var/log/candlepin/candlepin.log``
--------------------------------------------------------

ProductionLog - file ``/var/log/foreman/production.log``
--------------------------------------------------------

ProxyLog - file ``/var/log/foreman-proxy/proxy.log``
----------------------------------------------------

SatelliteLog - file ``/var/log/foreman-installer/satellite.log``
----------------------------------------------------------------

"""
from datetime import datetime

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.foreman_proxy_log)
class ProxyLog(LogFileOutput):
    """Class for parsing ``foreman-proxy/proxy.log`` file."""
    time_format = {
        'standard': '%d/%b/%Y:%H:%M:%S',  # 31/May/2016:09:57:34
        'error': '%Y-%m-%dT%H:%M:%S.%f'  # 2016-05-31T09:57:35.884636
    }


@parser(Specs.foreman_satellite_log)
class SatelliteLog(LogFileOutput):
    """Class for parsing ``foreman-installer/satellite.log`` file."""
    pass


@parser(Specs.foreman_production_log)
class ProductionLog(LogFileOutput):
    """Class for parsing ``foreman/production.log`` file."""
    pass


@parser(Specs.candlepin_log)
class CandlepinLog(LogFileOutput):
    """Class for parsing ``candlepin/candlepin.log`` file.

    Sample input::

        2016-09-09 13:45:52,650 [req=bd5a4284-d280-4fc5-a3d5-fc976b7aa5cc, org=] INFO org.candlepin.common.filter.LoggingFilter - Request: verb=GET, uri=/candlepin/consumers/f7677b4b-c470-4626-86a4-2fdf2546af4b
        2016-09-09 13:45:52,784 [req=bd5a4284-d280-4fc5-a3d5-fc976b7aa5cc, org=example_org] INFO  org.candlepin.common.filter.LoggingFilter - Response: status=200, content-type="application/json", time=134
        2016-09-09 13:45:52,947 [req=909ca4c5-f24e-4212-8f23-cc754d06ac57, org=] INFO org.candlepin.common.filter.LoggingFilter - Request: verb=GET, uri=/candlepin/consumers/f7677b4b-c470-4626-86a4-2fdf2546af4b/content_overrides
        2016-09-09 13:45:52,976 [req=909ca4c5-f24e-4212-8f23-cc754d06ac57, org=] INFO org.candlepin.common.filter.LoggingFilter - Response: status=200, content-type="application/json", time=29
        2016-09-09 13:45:53,072 [req=49becd26-5dfe-4d2f-8667-470519230d88, org=] INFO org.candlepin.common.filter.LoggingFilter - Request: verb=GET, uri=/candlepin/consumers/f7677b4b-c470-4626-86a4-2fdf2546af4b/release
        2016-09-09 13:45:53,115 [req=49becd26-5dfe-4d2f-8667-470519230d88, org=example_org] INFO  org.candlepin.common.filter.LoggingFilter - Response: status=200, content-type="application/json", time=43

    Each line is parsed into a dictionary with the following keys:

        * **raw_message(str)** - complete log line
        * **message(str)** - the body of the log
        * **timestamp(datetime)** - date and time of log as datetime object

    Examples:
        >>> cp_log_lines = cp_log.get('candlepin/consumers')
        >>> len(cp_log_lines)
        3
        >>> cp_log_lines[0].get('raw_message')
        '2016-09-09 13:45:52,650 [req=bd5a4284-d280-4fc5-a3d5-fc976b7aa5cc, org=] INFO org.candlepin.common.filter.LoggingFilter - Request: verb=GET, uri=/candlepin/consumers/f7677b4b-c470-4626-86a4-2fdf2546af4b'
        >>> cp_log_lines[0].get('message')
        '[req=bd5a4284-d280-4fc5-a3d5-fc976b7aa5cc, org=] INFO org.candlepin.common.filter.LoggingFilter - Request: verb=GET, uri=/candlepin/consumers/f7677b4b-c470-4626-86a4-2fdf2546af4b'
        >>> cp_log_lines[0].get('timestamp')
        datetime.datetime(2016, 9, 9, 13, 45, 52, 650000)
    """

    time_format = '%Y-%m-%d %H:%M:%S,%f'

    def _parse_line(self, line):
        # line format from /var/lib/tomcat/webapps/candlepin/WEB-INF/classes/logback.xml
        # <pattern>%d{ISO8601} [thread=%thread] [%X{requestType}=%X{requestUuid}, org=%X{org}, csid=%X{csid}] %-5p %c - %m%n</pattern>
        # http://logback.qos.ch/manual/layouts.html
        msg_info = {'raw_message': line}
        line_split = line.split(None, 2)
        if len(line_split) > 2:
            try:
                msg_info['timestamp'] = datetime.strptime(' '.join(line_split[:2]), self.time_format)
                msg_info['message'] = line_split[2]
            except ValueError:
                pass
        return msg_info


@parser(Specs.candlepin_error_log)
class CandlepinErrorLog(LogFileOutput):
    """
    Class for parsing ``candlepin/error.log`` file.

    Sample log contents::

        2016-09-07 13:56:49,001 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
        2016-09-07 14:07:33,735 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
        2016-09-07 14:09:55,173 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
        2016-09-07 15:20:33,796 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
        2016-09-07 15:27:34,367 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
        2016-09-07 16:49:24,650 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
        2016-09-07 18:07:53,688 [req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28, org=org_ray] ERROR org.candlepin.sync.Importer - Conflicts occurred during import that were not overridden:
        2016-09-07 18:07:53,690 [req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28, org=org_ray] ERROR org.candlepin.sync.Importer - [DISTRIBUTOR_CONFLICT]
        2016-09-07 18:07:53,711 [req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28, org=org_ray] ERROR org.candlepin.resource.OwnerResource - Recording import failure org.candlepin.sync.ImportConflictException: Owner has already imported from another subscription management application.

    Examples:
        >>> candlepin_log.get('req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28')[0]['raw_message']
        '2016-09-07 18:07:53,688 [req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28, org=org_ray] ERROR org.candlepin.sync.Importer - Conflicts occurred during import that were not overridden:'
        >>> from datetime import datetime
        >>> list(candlepin_log.get_after(datetime(2016, 9, 7, 16, 0, 0)))[0]['raw_message']
        '2016-09-07 16:49:24,650 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname'
    """
    pass


@parser(Specs.foreman_ssl_access_ssl_log)
class ForemanSSLAccessLog(LogFileOutput):
    """Class for parsing ``var/log/httpd/foreman-ssl_access_ssl.log`` file.

    Sample log contents::

        10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/385e688f-43ad-41b2-9fc7-593942ddec78 HTTP/1.1" 200 10736 "-" "-"
        10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/status HTTP/1.1" 200 263 "-" "-"
        10.185.73.33 - 8a31cd915917666001591d6fb44602a7 [27/Mar/2017:13:34:52 -0400] "GET /pulp/repos/Acme_Inc/Library/RHEL7_Sat_Cap        sule_Servers/content/dist/rhel/server/7/7Server/x86_64/os/repodata/repomd.xml HTTP/1.1" 200 2018 "-" "urlgrabber/3.10 yum/3.4.3"
        10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/4f8a39d0-38b6-4663-8b7e-03368be4d3ab/owner HTTP/1.1" 200 5159 "-"
        10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/385e688f-43ad-41b2-9fc7-593942ddec78/compliance HTTP/1.1" 200 5527
        10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/4f8a39d0-38b6-4663-8b7e-03368be4d3ab HTTP/1.1" 200 10695 "-" "-"


    Examples:
        >>> foreman_ssl_acess_log.get('consumers/385e688f-43ad-41b2-9fc7-593942ddec78')[0]['raw_message']
        '10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/385e688f-43ad-41b2-9fc7-593942ddec78 HTTP/1.1" 200 10736 "-" "-"'
    """
    time_format = '%d/%b/%Y:%H:%M:%S'
