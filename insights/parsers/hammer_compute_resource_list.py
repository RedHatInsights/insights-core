"""
HammerComputeResourceList - command ``hammer --interactive 0 --output json compute-resource list``
==================================================================================================

This module provides the class ``HammerComputeResourceList`` which parses the
compute resource data gathered using hammer tool in json format from a
satellite/foreman server.
"""
from insights import parser, JSONParser, CommandParser
from insights.specs import Specs


@parser(Specs.hammer_compute_resource_list)
class HammerComputeResourceList(CommandParser, JSONParser):
    """
    Parses compute resource data gathered using hammer tool in json format.

    Sample input data::

        [
            {
                "Id": 1,
                "Name": "kvm-server",
                "Provider": "Libvirt"
            },
            {
                "Id": 4,
                "Name": "vCenter-1",
                "Provider": "VMware"
            },
            {
                "Id": 3,
                "Name": "vCenter-2",
                "Provider": "VMware"
            }
        ]

    Examples:
        >>> type(compute_resource_list)
        <class 'insights.parsers.hammer_compute_resource_list.HammerComputeResourceList'>
        >>> isinstance(compute_resource_list.data, list)
        True
        >>> len(compute_resource_list.data)
        3
        >>> compute_resource_list.data[1]['Id']
        4
        >>> compute_resource_list.data[1]['Name'] == 'vCenter-1'
        True
        >>> compute_resource_list.data[1]['Provider'] == 'VMware'
        True
        >>> sorted(compute_resource_list.providers) == sorted(['Libvirt', 'VMware'])
        True
    """

    @property
    def providers(self):
        """
        Returns a list of unique compute providers used by compute resources.

        Returns:
            list: compute providers
        """
        return list({resource.get('Provider') for resource in self.data})
