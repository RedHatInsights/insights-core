"""
OpenVSwitchLogs - files ``ovsdb-server.log`` and ``ovs_vswitchd.log``
=====================================================================

A standard log file reader for logs written by OpenVSwitch.

The logs have a standard format::

    2016-03-08T02:10:01.155Z|01417|vlog|INFO|opened log file /var/log/openvswitch/ovs-vswitchd.log
    2016-03-08T02:20:05.425Z|01418|connmgr|INFO|br0<->unix: 1 flow_mods in the last 0 s (1 adds)
    2016-03-08T02:20:10.160Z|01419|connmgr|INFO|br0<->unix: 1 flow_mods in the last 0 s (1 deletes)
    2016-03-08T11:30:52.206Z|00013|fatal_signal|WARN|terminating with signal 15 (Terminated)

The ``get`` method breaks up log lines on the bar character ('|') into the
following fields:

* **timestamp** - the UTC time stamp
* **sequence** - the sequence number of this message
* **module** - the module in OpenVSwitch that emitted this error
* **level** - the level of error (INFO, WARN, ERROR)
* **message** - the rest of the message.

Each line of the resultant list is a dictionary with those fields.

Examples:

    >>> vswlog = shared[OVSDB_Server_Log]
    >>> 'fatal_signal' in vswlog
    True
    >>> vswlog.get('fatal_signal')
    [{'timestamp': '2016-03-08T11:30:52.206Z', 'sequence': '00013',
      'module': 'fatal_signal', 'level': 'WARN',
      'message': 'terminating with signal 15 (Terminated)',
      'raw_message': '2016-03-08T11:30:52.206Z|00013|fatal_signal|WARN|terminating with signal 15 (Terminated)']
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


class OpenVSwitchLog(LogFileOutput):
    """
    Template class for reading OpenVSwitch logs.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput` for
        more usage information.
    """
    time_format = '%Y-%m-%dT%H:%M:%S'
    _fieldnames = ['timestamp', 'sequence', 'module', 'level', 'message']

    def _parse_line(self, line):
        """
        Parse line into fields.
        """
        fields = line.split('|', 4)  # stop splitting after fourth | found
        line_info = {'raw_message': line}
        if len(fields) == 5:
            line_info.update(dict(zip(self._fieldnames, fields)))
        return line_info

    def __len__(self):
        return len(self.lines)


@parser(Specs.openvswitch_server_log)
class OVSDB_Server_Log(OpenVSwitchLog):
    """
    Parser for the ``ovsdb_server.log`` file, based on the OpenVSwitchLog
    class.
    """
    pass


@parser(Specs.openvswitch_daemon_log)
class OVS_VSwitchd_Log(OpenVSwitchLog):
    """
    Parser for the ``ovs-vswitchd.log`` file, based on the OpenVSwitchLog
    class.
    """
    pass
