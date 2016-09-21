from .. import MapperOutput, mapper, get_active_lines


@mapper("cinder.conf")
class CinderConf(MapperOutput):
    """
    a dict of cinder.conf
    Example:
    {
        "DEFAULT": {"storage_availability_zone":"nova", glance_num_retries: 0},
        "lvm": {"volumes_dir":"/var/lib/cider/columes"}
    }
    """
    @staticmethod
    def parse_content(content):

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
        return cinder_dict
