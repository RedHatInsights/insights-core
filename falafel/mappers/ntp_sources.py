from falafel.core.plugins import mapper


@mapper('chronyc_sources')
def get_chrony_sources(context):
    """
    Get source, mode and state for chrony
    """
    source_list = []
    for row in context.content[3:]:
        if row.strip():
            values = row.split(" ", 2)
            source_list.append({"source": values[1], "mode": values[0][0], "state": values[0][1]})
    if source_list:
        return source_list


@mapper('ntpq_pn')
def get_ntpd_sources(context):
    """
    Get source, flag for ntp
    """
    source_list = []
    for row in context.content[2:]:
        if row.strip():
            values = row.split(" ", 2)
            source_list.append({"source": values[0][1:], "flag": values[0][0]})
    if source_list:
        return source_list
