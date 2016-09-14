from falafel.core.plugins import mapper


@mapper("vdsm_id")
def get_vdsm_id(context):
    """
    Returns the UUID of this Host
    - E.g.: F7D9D983-6233-45C2-A387-9B0C33CB1306
    """
    for uuid in context.content:
        if not uuid.strip().startswith('#'):
            return uuid
