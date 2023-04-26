"""
GCPNetworkInterfaces
====================

This parser reads the output of a command
``curl -H "Metadata-Flavor: Google" "http://metadata/computeMetadata/v1/instance/network-interfaces/?recursive=true"``,
which is used to fetch external IP address information.

For more details, See: https://cloud.google.com/compute/docs/metadata/overview

"""
import json

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.gcp_network_interfaces)
class GCPNetworkInterfaces(CommandParser):
    """
    Class for parsing the GCP License Codes returned by command
    ``curl -H "Metadata-Flavor: Google" "http://metadata/computeMetadata/v1/instance/network-interfaces/?recursive=true"``,

    Typical Output of this command is::

        [
           {
              "accessConfigs":[
                 {
                    "externalIp":"34.67.41.222",
                    "type":"ONE_TO_ONE_NAT"
                 }
              ],
              "dnsServers":[
                 "169.254.169.254"
              ],
              "forwardedIps":[],
              "gateway":"10.128.0.1",
              "ip":"10.128.0.3",
              "ipAliases":[],
              "mac":"42:01:0a:80:00:03",
              "mtu":1460,
              "network":"projects/564421043971/networks/default",
              "subnetmask":"255.255.240.0",
              "targetInstanceIps":[]
           }
        ]

    Raises:
        SkipComponent: When content is empty or no parse-able content.
        ParseException: When the json is unable to be parsed

    Attributes:
        public_ips (list): A list containing public IPs in no particular order

    Examples:
        >>> gcp_network_interfaces.public_ips
        ["34.67.41.222"]
    """

    def parse_content(self, content):
        if not content or 'curl: ' in content[0]:
            raise SkipComponent()
        try:
            self.raw = json.loads(' '.join(content))
        except:
            raise ParseException("Unable to parse JSON")

        self.public_ips = []
        for nic in self.raw:
            if "accessConfigs" in nic:
                for ac in nic["accessConfigs"]:
                    if "externalIp" in ac:
                        self.public_ips.append(ac["externalIp"])

    def __repr__(self):
        return "public_ips: {i}, raw: {r}".format(i=self.public_ips, r=self.raw)
