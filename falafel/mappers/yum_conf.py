from .. import Mapper, mapper, get_active_lines


@mapper('yum.conf')
class YumConf(Mapper):
    """Class to parse the ``/etc/yum.conf`` file"""

    def __iter__(self):
        for section in self.data:
            yield section

    def get(self, key):
        return self.data.get(key)

    def parse_content(self, content):
        yum_conf_dict = {}
        section_dict = {}
        key = None
        for line in get_active_lines(content):
            if line.startswith('['):
                section_dict = {}
                yum_conf_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, _, value = line.partition("=")
                key = key.strip()
                if key in ('baseurl', 'gpgkey'):
                    section_dict[key] = [value.strip()]
                else:
                    section_dict[key] = value.strip()
            else:
                if key and isinstance(section_dict[key], list):
                    section_dict[key].append(line)

        self.data = yum_conf_dict

