from .. import Mapper, mapper, get_active_lines


@mapper("ceilometer.conf")
class CeilometerConf(Mapper):
    """
    a dict of ceilometer.conf
    Example:
    {
        "DEFAULT": {"http_timeout":"600",
                     debug: false
                     },
        "api": {"port":"8877",
               },

    }
    """

    def parse_content(self, content):
        ceilometer_dict = {}
        section_dict = {}
        for line in get_active_lines(content):
            if line.startswith("["):
                # new section beginning
                section_dict = {}
                ceilometer_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, value = line.split("=", 1)
                section_dict[key.strip()] = value.strip()
        self.data = ceilometer_dict
