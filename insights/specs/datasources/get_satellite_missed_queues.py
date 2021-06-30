import re

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.parsers.messages import Messages
from insights.combiners.satellite_version import SatelliteVersion
Messages.keep_scan('qpidd_node_not_found_errors', 'error Error on attach: Node not found')


@datasource(HostContext, SatelliteVersion, Messages)
def get_satellite_missed_pulp_agent_queues(broker):
    """
    This datasource provides the missed pulp agent queues information on satellite server.

    Note:
        This datasource may be executed using the following command:

        ``insights cat --no-header satellite_missed_pulp_agent_queues``

    Sample output::

        pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9:2018-01-16 00:06:13
        pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:16
        0

    Returns:
        str: The missed pulp agent queues and the mark if the data is truncated.

    Raises:
        SkipComponent: When the error doen't happen or the missed queues have been recreated.

    """
    def _parse_non_existing_queues_in_msg():
        agentq_date_re = re.compile(
            r'^(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[Protocol\] error Error on attach: Node not found: (?P<agentq>pulp.agent.[0-9a-f-]+)$'
        )
        agent_queue_last_date = {}
        for message in ms_obj.qpidd_node_not_found_errors:
            line = message['raw_message']
            info, msg = [i.strip() for i in line.split(': ', 1)]
            info_splits = info.rsplit(None, 2)
            if info_splits[2].startswith('qpidd'):
                # The timestamp from syslog doesn't contain the year, but the
                # message itself does - so use that.
                match = agentq_date_re.search(msg)
                if match:
                    agent_queue_last_date[match.group('agentq')] = match.group('date')
        return agent_queue_last_date

    def _get_content_host_uuid():
        cmd = '/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c "select uuid from katello_content_facets where uuid is not null;"'
        output = ctx.shell_out(cmd)
        host_uuids = []
        if len(output) > 3:
            for line in output[2:-1]:
                host_uuids.append(line.strip())
        return host_uuids

    def _get_qpid_queues():
        cmd = '/usr/bin/qpid-stat -q --ssl-certificate=/etc/pki/pulp/qpid/client.crt -b amqps://localhost:5671'
        output = ctx.shell_out(cmd)
        current_queues = []
        if len(output) > 3:
            current_queues = [line.split()[0].strip() for line in output[3:] if line.split()[0].startswith('pulp.agent')]
        return current_queues

    ms_obj = broker[Messages]
    ctx = broker[HostContext]
    missed_queues_in_log = _parse_non_existing_queues_in_msg()
    if missed_queues_in_log:
        host_uuids = _get_content_host_uuid()
        if host_uuids:
            qpid_queues = _get_qpid_queues()
            missed_queues = []
            too_more_data = 0
            for queue in missed_queues_in_log:
                if queue.split('.')[-1] in host_uuids and queue not in qpid_queues:
                    missed_queues.append('%s:%s' % (queue, missed_queues_in_log[queue]))
                    # only return 10 missed queues in case too long data can't be rendered
                    if len(missed_queues) >= 10:
                        too_more_data = 1
                        break
            if missed_queues:
                missed_queues.append(str(too_more_data))
                return DatasourceProvider(missed_queues, relative_path='insights_commands/satellite_missed_qpid_queues')
    raise SkipComponent
