from falafel.core.plugins import mapper
from falafel.core import MapperOutput


@mapper("corosync")
class CoroSyncConfig(MapperOutput):

    @classmethod
    def parse_context(cls, context):

        """
        Parse /etc/sysconfig/corosync
        return dict like {'COROSYNC_OPTIONS': '', 'COROSYNC_INIT_TIMEOUT': '60'}
        """

        corosync_dict = {}
        for line in context.content:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            if "=" in line:
                (key, value) = line.split("=", 1)
                corosync_dict[key.strip()] = value.strip().replace('"', "")
        return cls(corosync_dict, context.path)
