from .. import Mapper, mapper, get_active_lines


@mapper("corosync")
class CoroSyncConfig(Mapper):

    def parse_content(self, content):
        """
        Parse /etc/sysconfig/corosync
        return dict like {'COROSYNC_OPTIONS': '', 'COROSYNC_INIT_TIMEOUT': '60'}
        """

        self.data = {}
        for line in get_active_lines(content):
            if "=" in line:
                (key, value) = line.split("=", 1)
                self.data[key.strip()] = value.strip().replace('"', "")
