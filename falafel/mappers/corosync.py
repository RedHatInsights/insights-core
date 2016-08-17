from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines


@mapper("corosync")
class CoroSyncConfig(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        Parse /etc/sysconfig/corosync
        return dict like {'COROSYNC_OPTIONS': '', 'COROSYNC_INIT_TIMEOUT': '60'}
        """

        corosync_dict = {}
        for line in get_active_lines(content):
            if "=" in line:
                (key, value) = line.split("=", 1)
                corosync_dict[key.strip()] = value.strip().replace('"', "")
        return corosync_dict
