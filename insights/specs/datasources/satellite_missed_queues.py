import re

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.combiners.satellite_version import SatelliteVersion
from insights.specs import Specs
from insights.core.filters import add_filter


NODE_NOT_FOUND_ERROR = 'error Error on attach: Node not found'
add_filter(Specs.messages, NODE_NOT_FOUND_ERROR)


class LocalSpecs(Specs):
    """ Local specs used only by get_satellite_missed_pulp_agent_queues datasources """

    content_host_uuids = simple_command(
        '/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c "select uuid from katello_content_facets where uuid is not null;"',
        deps=[SatelliteVersion]
    )
    qpid_queues = simple_command(
        '/usr/bin/qpid-stat -q --ssl-certificate=/etc/pki/pulp/qpid/client.crt -b amqps://localhost:5671',
        deps=[SatelliteVersion]
    )


@datasource(LocalSpecs.content_host_uuids, LocalSpecs.qpid_queues, Specs.messages, HostContext, SatelliteVersion)
def satellite_missed_pulp_agent_queues(broker):
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
        str: All the missed pulp agent queues and the boolean mark if the data is
            truncated in the last line. If the value of last line is 0,
            it means all the missed queues are returned. If the value of the
            last line is 1, it means there are a lot of missed queues, to
            avoid render error, only the first 10 missed queues are returned.

    Raises:
        SkipComponent: When the error doen't happen or the missed queues have been recreated.

    """
    def _parse_non_existing_queues_in_msg():
        agentq_date_re = re.compile(
            r'^(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[Protocol\] error Error on attach: Node not found: (?P<agentq>pulp.agent.[0-9a-f-]+)$'
        )
        agent_queue_last_date = {}
        ms_obj = broker[Specs.messages]
        for line in ms_obj.stream():
            if NODE_NOT_FOUND_ERROR in line:
                info, msg = [i.strip() for i in line.split(': ', 1)]
                info_splits = info.rsplit(None, 2)
                if len(info_splits) >= 3 and info_splits[2].startswith('qpidd'):
                    # The timestamp from syslog doesn't contain the year, but the
                    # message itself does - so use that.
                    match = agentq_date_re.search(msg)
                    if match:
                        agent_queue_last_date[match.group('agentq')] = match.group('date')
        return agent_queue_last_date

    def _get_content_host_uuid():
        output = broker[LocalSpecs.content_host_uuids].content
        host_uuids = []
        if len(output) > 3:
            for line in output[2:-1]:
                host_uuids.append(line.strip())
        return host_uuids

    def _get_qpid_queues():
        output = broker[LocalSpecs.qpid_queues].content
        current_queues = []
        if len(output) > 3:
            current_queues = [line.split()[0].strip() for line in output[3:] if line.split()[0].startswith('pulp.agent')]
        return current_queues

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
