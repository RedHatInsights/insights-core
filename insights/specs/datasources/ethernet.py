"""
Custom datasource for gathering a list of the ethernet interface names.
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import simple_command
from insights.parsers.nmcli import NmcliConnShow
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by ethernet_interfaces datasource. """
    ip_link = simple_command("/sbin/ip -o link")


@datasource(LocalSpecs.ip_link, HostContext)
def interfaces(broker):
    """
    This datasource provides a list of the ethernet interfaces available.

    Typical content of the spec is::

        1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000\\    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:13:14:b5 brd ff:ff:ff:ff:ff:ff
        3: enp8s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:e5:11:d4 brd ff:ff:ff:ff:ff:ff
        4: enp1s0.2@enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:13:14:b5 brd ff:ff:ff:ff:ff:ff
        5: ib0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 4092 qdisc mq state DOWN group default qlen 256\\    link/infiniband 00:01:02:03:fd:90:0:00:00:00:00:00:ef:0d:8b:02:01:d9:82:fd

    Note:
        This datasource may be executed using the following command:

        ``insights cat --no-header ethernet_interfaces``

    Sample data returned::

        ['enp1s0', 'enp8s0', 'enp1s0.2']

    Returns:
        list: List of the ethernet interfaces available.

    Raises:
        SkipComponent: When there is not any content.
    """
    content = broker[LocalSpecs.ip_link].content
    if content:
        ifaces = []
        for x in content:
            # Only process lines that have link/ether, this should exclude non ethernet devices.
            if "link/ether" in x:
                # Split first on : the interface name should be the second entry.
                # Then split again on @ since vlans append @ and the parent interface name to the end.
                ifaces.append(x.split(':')[1].split('@')[0].strip())

        if ifaces:
            return sorted(ifaces)

    raise SkipComponent


@datasource(NmcliConnShow, HostContext)
def team_interfaces(broker):
    """
    This datasource provides a list of the team device.

    Sample data returned::

        ['team0', 'team1']

    Returns:
        list: List of the team device.

    Raises:
        SkipComponent: When there is not any team interfaces.
    """

    content = broker[NmcliConnShow].data
    if content:
        team_ifaces = []
        for x in content:
            if 'team' in x['TYPE'] and x['DEVICE'] != '--':
                team_ifaces.append(x['DEVICE'])

        if team_ifaces:
            return sorted(team_ifaces)

    raise SkipComponent
