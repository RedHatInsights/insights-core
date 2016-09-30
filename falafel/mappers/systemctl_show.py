from .. import MapperOutput
from .. import mapper
from .. import get_active_lines


@mapper('systemctl_cinder-volume')
class SystemctlShowCinderVolume(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        Sample Input:
            TimeoutStartUSec=1min 30s
            LimitNOFILE=65536
            LimitMEMLOCK=
            LimitLOCKS=18446744073709551615

        Sample Output:
            {"LimitNOFILE"     : "65536",
            "TimeoutStartUSec" : "1min 30s",
            "LimitLOCKS"       : "18446744073709551615"}

        In CMD's output, empty properties are suppressed by default.
        We will also suppressed empty properties in return data.
        """
        data = {}

        for line in get_active_lines(content):
            key, _, value = line.strip().partition("=")
            if value:
                data[key.strip()] = value.strip()

        return data
