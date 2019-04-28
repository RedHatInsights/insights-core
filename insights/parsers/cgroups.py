"""
Cgroups - File ``/proc/cgroups``
================================

This parser reads the content of ``/proc/cgroups``.
This file shows the control groups information of system.

Sample ``/proc/cgroups`` file::

    #subsys_name	hierarchy	num_cgroups	enabled
    cpuset	10	48	1
    cpu	2	232	1
    cpuacct	2	232	1
    memory	5	232	1
    devices	6	232	1
    freezer	3	48	1
    net_cls	4	48	1
    blkio	9	232	1
    perf_event	8	48	1
    hugetlb	11	48	1
    pids	7	232	1
    net_prio	4	48	1


Examples:

    >>> i_cgroups.get_num_cgroups("memory")
    232
    >>> i_cgroups.is_subsys_enabled("memory")
    True
    >>> i_cgroups.data[0].get('hierarchy')
    '10'

"""

from .. import parser, CommandParser
from insights.specs import Specs
from . import ParseException, parse_delimited_table


@parser(Specs.cgroups)
class Cgroups(CommandParser):
    """
    Class ``Cgroups`` parses the content of the ``/proc/cgroups``.

    Attributes:
        data (list): A list of the subsystem cgroup information

    """

    def parse_content(self, content):
        # replace #subsys_name to subsys_name
        content[0] = content[0].replace("#", '')
        table = parse_delimited_table(content)
        self.data = [dict((k.lower(), v) for (k, v) in item.items()) for item in table]

    def get_num_cgroups(self, i_subsys_name):
        """
        Get value of cgroup number for specified subsystem, raise exception if keyword not found.

        Example:

            >>> i_cgroups.get_num_cgroups("memory")
            232
            >>> i_cgroups.get_num_cgroups('hugetlb')
            48

        Args:

            i_subsys_name (str): specified subsystem name.

        Returns:

            value (int): Int value of the specified subsystem cgroups
        """
        for subsys_item in self.data:
            if subsys_item["subsys_name"] == i_subsys_name:
                return int(subsys_item["num_cgroups"])
        # raise exception if give the wrong subsys_name
        raise ParseException("Wrong subsys_name: {0}".format(i_subsys_name))

    def is_subsys_enabled(self, i_subsys_name):
        """
        Get enable or not of cgroup of specified subsystem, raise exception if keyword not found.

        Example:

            >>> i_cgroups.is_subsys_enabled("memory")
            True
            >>> i_cgroups.is_subsys_enabled('hugetlb')
            True

        Args:

            i_subsys_name (str): specified subsystem name.

        Returns:

            value (boolean): Return True if the cgroup of specified subsystem is enabled, else return False
        """
        for subsys_item in self.data:
            if subsys_item["subsys_name"] == i_subsys_name:
                return subsys_item["enabled"] == "1"
        # raise exception if give the wrong subsys_name
        raise ParseException("Wrong subsys_name: {0}".format(i_subsys_name))
