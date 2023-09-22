"""
OVSvsctlListBridge - command ``/usr/bin/ovs-vsctl list bridge``
===============================================================

This module provides class ``OVSvsctlListBridge`` for parsing the
output of command ``ovs-vsctl list bridge``.

.. note::
    Please refer to its super-class :class:`insights.parsers.ovs_vsctl_list.OVSvsctlList`
    for more details.

.. warning::
    This parser `OVSvsctlListBridge` is deprecated, please use
    :py:class:`insights.ovs_vsctl.OVSvsctlListBridge` instead.
"""

from insights import parser
from insights.parsers.ovs_vsctl import OVSvsctlList
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.ovs_vsctl_list_bridge)
class OVSvsctlListBridge(OVSvsctlList):
    """
    .. warning::
        This parser `OVSvsctlListBridge` is deprecated, please use
        :py:class:`insights.ovs_vsctl.OVSvsctlListBridge` instead.

    Class to parse output of command ``ovs-vsctl list bridge``.
    Generally, the data is in key:value format with values having
    data types as string, numbers, list or dictionary.
    The class provides attribute ``data`` as list with lines parsed
    line by line based on keys for each bridge.

    Sample command output::

        name                : br-int
        other_config        : {disable-in-band="true", mac-table-size="2048"}
        name                : br-tun
        other_config        : {}

    Examples:
        >>> bridge_lists[0]["name"]
        'br-int'
        >>> bridge_lists[0]["other_config"]["mac-table-size"]
        '2048'
        >>> bridge_lists[0]["other_config"]["disable-in-band"]
        'true'
        >>> bridge_lists[1].get("name")
        'br-tun'
        >>> len(bridge_lists[1]["other_config"]) == 0
        True

    Attributes:
        data (list): A list containing dictionary elements where each
                     element contains the details of a bridge.

    Raises:
        SkipComponent: When file is empty.
    """
    def __init__(self, *args, **kwargs):
        deprecated(
            OVSvsctlListBridge,
            "Please use the :class:`insights.ovs_vsctl.OVSvsctlListBridge` instead.",
            "3.3.0"
        )
        super(OVSvsctlListBridge, self).__init__(*args, **kwargs)
