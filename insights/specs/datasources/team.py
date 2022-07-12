"""
Custom datasource for gathering a list of the team interface names.
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.nmcli import NmcliConnShow


@datasource(NmcliConnShow, HostContext)
def team_filter(broker):
    """
    This datasource provides a list of the team interfaces available.

    Typical content of the spec is::

        NAME      UUID                                  TYPE      DEVICE
        enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3
        virbr0    7c7dec66-4a8c-4b49-834a-889194b3b83c  bridge    virbr0
        test-net  f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --
        team0     bf000427-d9f1-432f-819d-257edb86c6fb  team      team0
        ens3      1b1f5c95-1026-4699-95e5-2cd5baa033c3  ethernet  ens3
        ens8      a2c39643-b356-435a-955c-50cef6b36052  ethernet  ens8
        team1     ca07b1cf-b293-4871-b255-17f1abfa991d  team      team1

    Sample data returned::

        ['team0', 'team1']

    Returns:
        list: List of the team interfaces available.

    Raises:
        SkipComponent: When there is not any content.
    """

    content = broker[NmcliConnShow].data
    if content:
        ifaces = []
        for x in content:
            if 'team' in x['TYPE']:
                ifaces.append(x['DEVICE'])

        if ifaces:
            return sorted(ifaces)

    raise SkipComponent
