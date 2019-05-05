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
    >>> i_cgroups.subsystems["memory"]["enabled"]
    '1'

"""

from .. import parser, Parser
from insights.specs import Specs
from . import parse_delimited_table


@parser(Specs.cgroups)
class Cgroups(Parser):
    """
    Class ``Cgroups`` parses the content of the ``/proc/cgroups``.

    Attributes:
        data (list): A list of the subsystem cgroup information
        subsystems (dict): A dict of all subsystems, key is subsystem name and value is dict with keys: hierarchy, num_cgroups, enabled
    """

    def parse_content(self, content):
        # replace #subsys_name to subsys_name
        self.data = parse_delimited_table(content,
                                          heading_ignore=['#subsys_name', 'hierarchy'],
                                          header_substitute=[('#subsys_name', 'subsys_name')])
        self.subsystems = {}
        for subsys in self.data:
            self.subsystems[subsys.pop("subsys_name")] = subsys

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

        Raises:
            KeyError: Exception is raised if given subsystem name is wrong

        """
        if i_subsys_name in self.subsystems:
            return int(self.subsystems[i_subsys_name]["num_cgroups"])
        # raise keyerror exception if give the wrong subsys_name
        raise KeyError("Gave wrong subsys_name: {0}".format(i_subsys_name))

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

        Raises:
            KeyError: Exception is raised if given subsystem name is wrong

        """
        if i_subsys_name in self.subsystems:
            return self.subsystems[i_subsys_name]["enabled"] == "1"
        # raise keyerror exception if give the wrong subsys_name
        raise KeyError("Gave wrong subsys_name: {0}".format(i_subsys_name))
