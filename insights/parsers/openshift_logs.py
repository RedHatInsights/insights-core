"""
OpenShiftLogs - command ``oc logs``
===================================

A standard log command reader for logs from command ``oc logs dc/XXX`` .
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.oc_logs_dc_router)
class OpenShiftDcRouterLogs(LogFileOutput):
    """
    Class for reading OpenShiftDcRouterLogs logs.

    The logs have a standard format::

        2018-05-15T03:19:42.020507000Z I0515 03:19:42.006017       1 template.go:246] Starting template router (v3.6.173.0.112)
        2018-05-15T03:19:42.974500000Z I0515 03:19:42.970212       1 router.go:554] Router reloaded:
        2018-05-15T03:19:42.974827000Z  - Checking http://localhost:80 ...
        2018-05-15T03:19:42.975175000Z  - Health check ok : 0 retry attempt(s).
        2018-05-15T03:19:42.975431000Z I0515 03:19:42.970321       1 router.go:240] Router is including routes in all namespaces

    The log would be splitted into following fields:

    * **timestamp** - the UTC time stamp
    * **message** - the rest of the message.

    Examples:
        >>> len(logs)
        14
        >>> logs.get("Router reloaded")[0]["timestamp"]
        '2018-05-15T03:19:42.974500000Z'
        >>> logs.get("Checking http://localhost:80")[2]["message"]
        ' - Checking http://localhost:80 ...'
    """
    time_format = '%Y-%m-%dT%H:%M:%S'
    _fieldnames = ['timestamp', 'message']

    def _parse_line(self, line):
        """
        Parse line into fields.
        """
        fields = line.split(' ', 1)
        line_info = {'raw_message': line}
        line_info.update(dict(zip(self._fieldnames, fields)))
        return line_info

    def __len__(self):
        return len(self.lines)
