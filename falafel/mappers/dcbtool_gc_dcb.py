from falafel.core.plugins import mapper


@mapper("dcbtool_gc_dcb")
def dcbtool_gc_dcb(context):
    """
    Parse Lines from the `dcbtool gc eth1 dcb` to check DCBX is enable
    Input:

    Command:    Get Config
    Feature:    DCB State
    Port:       eth0
    Status:     Off
    DCBX Version: FORCED CIN

    Output is a dict:
    {
        "command": "Get Config",
        "feature": "DCB State",
        "port": "eth0",
        "status": "Off"
        "dcbx_version":"FORCED CIN"
    }

    If error encounter, return a dict not contain any key.
    """
    if "Connection refused" in context.content[0]:
        return {}
    return {
        content[0].lower().strip().replace(" ", "_"): content[1].strip()
        for content in
        [line.split(":", 1) for line in context.content]
    }
