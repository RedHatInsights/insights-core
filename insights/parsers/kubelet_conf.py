"""
KubeletConf file ``/etc/kubernetes/kubelet.conf``
=================================================
This parser is used to parse ``/etc/kubernetes/kubelet.conf
file information from sosreport.
"""
from insights.core.plugins import parser
from insights.core import JSONParser
from insights.specs import Specs


@parser(Specs.kubelet_conf)
class KubeletConf(JSONParser):
    """Class to parse ``/etc/kubernetes/kubelet.conf`` file"""
