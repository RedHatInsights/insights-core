from .. import mapper


@mapper('cpuinfo_max_freq')
def cpu_max_freq(context):
    """
    Returns an integer representing the maximum frequency in KHZ
    - E.g.: 3200000
    """
    return int(context.content[0].strip())
