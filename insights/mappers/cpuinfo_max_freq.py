"""
cpuinfo_max_freq - file ``/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq``
=================================================================================

A simple mapper to turn the maximum frequency of the first CPU, given in
the above file, into an integer.

Examples:
    >>> max_freq = shared[cpu_max_freq]
    >>> max_freq
    3200000
"""

from .. import mapper


@mapper('cpuinfo_max_freq')
def cpu_max_freq(context):
    """
    Returns an integer representing the maximum frequency in KHZ
    - e.g.: ``3200000``
    """
    return int(context.content[0].strip())
