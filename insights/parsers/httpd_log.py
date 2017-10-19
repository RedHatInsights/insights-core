"""
httpd_log - Files /var/log/httpd/\*_log
=======================================

Modules for parsing the log files of httpd service

Note:
    Please refer to its super-class ``LogFileOutput``

"""

from .. import LogFileOutput, parser
from insights.specs import httpd_access_log
from insights.specs import httpd_error_log
from insights.specs import httpd_ssl_access_log
from insights.specs import httpd_ssl_error_log


@parser(httpd_ssl_error_log)
class HttpdSSLErrorLog(LogFileOutput):
    """Class for parsing httpd ``ssl_error_log`` file."""
    time_format = '%b %d %H:%M:%S.%f %Y'


@parser(httpd_error_log)
class HttpdErrorLog(LogFileOutput):
    """Class for parsing httpd ``error_log`` file."""
    time_format = '%b %d %H:%M:%S.%f %Y'


@parser(httpd_ssl_access_log)
class HttpdSSLAccessLog(LogFileOutput):
    """Class for parsing httpd ``ssl_access_log`` file."""
    time_format = '%d/%b/%Y:%H:%M:%S'


@parser(httpd_access_log)
class HttpdAccessLog(LogFileOutput):
    """Class for parsing httpd ``access_log`` file."""
    time_format = '%d/%b/%Y:%H:%M:%S'
