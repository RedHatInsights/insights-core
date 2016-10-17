from .. import Mapper, mapper, get_active_lines


@mapper("cinder.conf")
class CinderConf(Mapper):
    """
    a dict of cinder.conf
    Example:
    {
        "DEFAULT": {"storage_availability_zone":"nova", glance_num_retries: 0},
        "lvm": {"volumes_dir":"/var/lib/cider/columes"}
    }
    """
    def parse_content(self, content):

        cinder_dict = {}
        section_dict = {}
        for line in get_active_lines(content):
            if line.startswith("["):
                # new section beginning
                section_dict = {}
                cinder_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, value = line.split("=", 1)
                section_dict[key.strip()] = value.strip()
        self.data = cinder_dict
