from .. import mapper, Mapper, get_active_lines


@mapper("dcbtool_gc_dcb")
class Dcbtool(Mapper):
    """
    Parse Lines from the `dcbtool gc eth1 dcb` to check DCBX if enabled

    Successful completion of the command returns data like:

        Command:    Get Config
        Feature:    DCB State
        Port:       eth0
        Status:     Off
        DCBX Version: FORCED CIN

    Returns
    -------

    The ``data`` member of the class is a ``dict`` that
    reflects the above content, e.g.:

    .. code-block:: python

        {
            "command": "Get Config",
            "feature": "DCB State",
            "port": "eth0",
            "status": "Off"
            "dcbx_version":"FORCED CIN"
        }

    If a "Connection refused" error is encountered,
    an empty dictionary is returned`.
    """
    def parse_content(self, content):
        self.data = {}
        if "Connection refused" in content[0]:
            return

        for line in get_active_lines(content):
            key, value = line.split(":", 1)
            key = key.lower().replace(" ", "_")
            self.data[key] = value.strip()


@mapper("dcbtool_gc_dcb")
def dcbtool_gc_dcb(context):
    """Deprecated, use ``Dcbtool`` instead."""
    return Dcbtool(context).data
