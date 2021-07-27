"""
SatelliteMissedQueues - datasource ``satellite_missed_pulp_agent_queues``
=========================================================================
"""
from insights import parser, Parser
from insights.specs import Specs
from insights import SkipComponent


@parser(Specs.satellite_missed_pulp_agent_queues)
class SatelliteMissedQueues(Parser):
    """This parser parses the output of ``satellite_missed_pulp_agent_queues`` datasource.

    Typical output from the datasource is::

        pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9:2018-01-16 00:06:13
        pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:16
        0

    Examples:
        >>> satellite_queues.truncated
        False
        >>> 'pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9' in satellite_queues.missed_queues
        True
        >>> satellite_queues.missed_queues['pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9']
        '2018-01-16 00:06:13'

    Attributes:
        missed_queues(dict): Satellite missed pulp agent queues.
        truncated(bool): The missed queues truncated or not.

    Raises:
        SkipComponent: when no missed queues or the content isn't in expected format.
"""
    def parse_content(self, content):
        self.missed_queues = {}
        self.truncated = None
        if len(content) >= 2:
            for line in content[:-1]:
                if ':' not in line:
                    raise SkipComponent
                parts = line.split(':', 1)
                self.missed_queues[parts[0]] = parts[1]
            if content[-1].strip() in ['0', '1']:
                self.truncated = True if content[-1].strip() == '1' else False
        if not self.missed_queues or self.truncated is None:
            raise SkipComponent
