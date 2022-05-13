import doctest
from insights.parsers import neutron_l3_agent_conf
from insights.parsers.neutron_l3_agent_conf import NeutronL3AgentIni
from insights.tests import context_wrap


L3_AGENT_INI = """
[DEFAULT]

#
# From neutron.base.agent
#

# Name of Open vSwitch bridge to use (string value)
ovs_integration_bridge = br-int

# Uses veth for an OVS interface or not. Support kernels with limited namespace
# support (e.g. RHEL 6.5) so long as ovs_use_veth is set to True. (boolean
# value)
ovs_use_veth = false

# The driver used to manage the virtual interface. (string value)
#interface_driver = <None>
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver

# Timeout in seconds for ovs-vsctl commands. If the timeout expires, ovs
# commands will fail with ALARMCLOCK error. (integer value)
ovs_vsctl_timeout = 10

#
# From neutron.l3.agent
#

# The working mode for the agent. Allowed modes are: 'legacy' - this preserves
# the existing behavior where the L3 agent is deployed on a centralized
# networking node to provide L3 services like DNAT, and SNAT. Use this mode if
# you do not want to adopt DVR. 'dvr' - this mode enables DVR functionality and
# must be used for an L3 agent that runs on a compute host. 'dvr_snat' - this
# enables centralized SNAT support in conjunction with DVR.  This mode must be
# used for an L3 agent running on a centralized node (or in single-host
# deployments, e.g. devstack) (string value)
# Allowed values: dvr, dvr_snat, legacy
agent_mode = dvr

# TCP Port used by Neutron metadata namespace proxy. (port value)
# Minimum value: 0
# Maximum value: 65535
metadata_port = 9697

# Send this many gratuitous ARPs for HA setup, if less than or equal to 0, the
# feature is disabled (integer value)
#send_arp_for_ha = 3

# Allow running metadata proxy. (boolean value)
enable_metadata_proxy = true

# DEPRECATED: Name of bridge used for external network traffic. When this
# parameter is set, the L3 agent will plug an interface directly into an
# external bridge which will not allow any wiring by the L2 agent. Using this
# will result in incorrect port statuses. This option is deprecated and will be
# removed in Ocata. (string value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
external_network_bridge =

#
# From oslo.log
#

# If set to true, the logging level will be set to DEBUG instead of the default
# INFO level. (boolean value)
# Note: This option can be changed without restarting.
debug = False

# Defines the format string for %%(asctime)s in log records. Default:
# %(default)s . This option is ignored if log_config_append is set. (string
# value)
log_date_format = %Y-%m-%d %H:%M:%S

[AGENT]

#
# From neutron.base.agent
#

# Seconds between nodes reporting state to server; should be less than
# agent_down_time, best if it is half or less than agent_down_time. (floating
# point value)
report_interval = 30

# Log agent heartbeats (boolean value)
log_agent_heartbeats = false

# Availability zone of this node (string value)
availability_zone = nova
""".strip()


def test_neutron_l3_agent_ini():
    nla_ini = NeutronL3AgentIni(context_wrap(L3_AGENT_INI))
    assert nla_ini.has_option("AGENT", "log_agent_heartbeats")
    assert nla_ini.get("DEFAULT", "agent_mode") == "dvr"
    assert nla_ini.getint("DEFAULT", "metadata_port") == 9697


def test_doc():
    env = {"l3_agent_ini": NeutronL3AgentIni(context_wrap(L3_AGENT_INI, path="/etc/neutron/l3_agent.ini"))}
    failed, total = doctest.testmod(neutron_l3_agent_conf, globs=env)
    assert failed == 0
