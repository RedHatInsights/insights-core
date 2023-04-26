import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers.gcp_network_interfaces import GCPNetworkInterfaces
from insights.tests import context_wrap

GCP_NIC_1 = """
[{
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
}]
"""
GCP_NIC_2 = '[]'

GCP_NIC_CURL_1 = """
curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out
""".strip()
GCP_NIC_CURL_2 = """
curl: (7) couldn't connect to host
""".strip()
GCP_NIC_CURL_3 = """
curl: (28) connect() timed out!
""".strip()


def test_azure_instance_place_ab_other():
    with pytest.raises(SkipComponent):
        GCPNetworkInterfaces(context_wrap(GCP_NIC_CURL_1))

    with pytest.raises(SkipComponent):
        GCPNetworkInterfaces(context_wrap(GCP_NIC_CURL_2))

    with pytest.raises(SkipComponent):
        GCPNetworkInterfaces(context_wrap(GCP_NIC_CURL_3))

    with pytest.raises(SkipComponent):
        GCPNetworkInterfaces(context_wrap(''))


def test_gcp_public_ips():
    gcp_nics = GCPNetworkInterfaces(context_wrap(GCP_NIC_1))
    assert gcp_nics.public_ips == ["34.67.41.222"]
    assert gcp_nics.raw[0]["dnsServers"] == ["169.254.169.254"]

    gcp_nics = GCPNetworkInterfaces(context_wrap(GCP_NIC_2))
    assert gcp_nics.public_ips == []
