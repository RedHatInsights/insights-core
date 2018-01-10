"""
Apache httpd logs
=================

Modules for parsing the log files of httpd service.  Parsers include:

HttpdSSLErrorLog - file ``ssl_error_log``
-----------------------------------------

HttpdErrorLog - file ``error_log``
----------------------------------

HttpdSSLAccessLog - file ``ssl_access_log``
-------------------------------------------

HttpdAccessLog - file ``access_log``
------------------------------------

.. note::
    Please refer to the super-class :py:class:`insights.core.LogFileOutput`
    for more usage information.

"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.httpd_ssl_error_log)
class HttpdSSLErrorLog(LogFileOutput):
    """Class for parsing httpd ``ssl_error_log`` file."""
    time_format = '%b %d %H:%M:%S.%f %Y'


@parser(Specs.httpd_error_log)
class HttpdErrorLog(LogFileOutput):
    """Class for parsing httpd ``error_log`` file."""
    time_format = '%b %d %H:%M:%S.%f %Y'


@parser(Specs.httpd_ssl_access_log)
class HttpdSSLAccessLog(LogFileOutput):
    """Class for parsing httpd ``ssl_access_log`` file."""
    time_format = '%d/%b/%Y:%H:%M:%S'


@parser(Specs.httpd_access_log)
class HttpdAccessLog(LogFileOutput):
    """Class for parsing httpd ``access_log`` file."""
    time_format = '%d/%b/%Y:%H:%M:%S'
