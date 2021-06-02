"""
Custom datasources for Tomcat information
"""
import re

from insights.core.dr import SkipComponent
from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.specs import Specs


@datasource(Specs.ps_auxww, HostContext)
def base_paths(broker):
    """
    Function to search the output of ``ps auxww`` to find all running tomcat
    processes and extract the base path where the process was started.

    Returns:
        list: List of the paths to each running process
    """
    ps = broker[Specs.ps_auxww].content
    results = []
    findall = re.compile(r"\-Dcatalina\.base=(\S+)").findall
    for p in ps:
        found = findall(p)
        if found:
            # Only get the path which is absolute
            results.extend(f for f in found if f[0] == '/')

    if results:
        return list(set(results))

    raise SkipComponent
