import re

from insights.core.dr import SkipComponent


def base_paths(ps_auxww):
    """
    Function to search the output of ``ps auxww`` to find all running tomcat
    processes and extract the base path where the process was started.

    Returns:
        list: List of the paths to each running process
    """
    ps = ps_auxww.content
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
