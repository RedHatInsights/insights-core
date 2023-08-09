"""
Custom datasource to get the list of the rsyslog errorfile paths.
"""

from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.combiners.rsyslog_confs import RsyslogAllConf
from insights.core.exceptions import SkipComponent


@datasource(RsyslogAllConf, HostContext)
def rsyslog_errorfile(broker):
    """
    This datasource provides the list of the rsyslog errorfile paths.

    Sample data returned::

        '/var/log/omelasticsearch.log /var/log/oversized.log'

    Returns:
        string: string of the errorfile paths that separated by a whitespace.

    Raises:
        SkipComponent: When 'errorfile' is not configured.
    """

    rsyslog_confs = broker[RsyslogAllConf]
    if rsyslog_confs:
        result_list = []
        for conf_path in rsyslog_confs:
            for line in rsyslog_confs[conf_path]:
                if 'errorfile' in line and 'action' in line:
                    paths = line.split('errorfile')
                    for i in range(1, len(paths)):
                        errorfile_path = paths[i].split('"')[1]
                        result_list.append(errorfile_path)
        if result_list:
            return ' '.join(result_list)

    raise SkipComponent
