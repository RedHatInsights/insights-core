"""
NeutronL3AgentLog - file ``/var/log/neutron/l3-agent.log``
==========================================================
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.neutron_l3_agent_log)
class NeutronL3AgentLog(LogFileOutput):
    """
      Parse the ``/var/log/neutron/l3-agent.log`` file.

      .. note::
          Please refer to its super-class :class:`insights.core.LogFileOutput` for more
          details.

      Sample log lines::

          2017-09-17 10:05:06.241 141544 INFO neutron.agent.l3.ha [-] Router 01d51830-0e3e-4100-a891-efd7dbc000b1 transitioned to backup
          2017-09-17 10:05:07.828 141544 WARNING neutron.agent.linux.iptables_manager [-] Duplicate iptables rule detected. This may indicate a bug in the the iptables rule generation code. Line: -A neutron-l3-agent-INPUT -p tcp -m tcp --dport 9697 -j DROP
          2017-09-17 10:05:07.829 141544 WARNING neutron.agent.linux.iptables_manager [-] Duplicate iptables rule detected. This may indicate a bug in the the iptables rule generation code. Line: -A neutron-l3-agent-INPUT -m mark --mark 0x1/0xffff -j ACCEP

      Examples:
          >>> len(agent_log.get("Duplicate iptables rule detected")) == 2
          True
          >>> from datetime import datetime
          >>> len(list(agent_log.get_after(datetime(2017, 2, 17, 10, 5, 7))))
          3

      """
    pass
