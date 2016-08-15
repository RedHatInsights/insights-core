from falafel.core.plugins import mapper
from falafel.mappers import get_active_lines
from falafel.core import MapperOutput, computed

@mapper("cinder.conf")
class CinderConf(MapperOutput):
    @classmethod
    def parse_context(cls, context):
        """
            parsing cinder.conf and return dict.
            :return: a dict(dict)   Example:  {"DEFAULT": {"storage_availability_zone":"nova", glance_num_retries: 0},
            "lvm": {"volumes_dir":"/var/lib/cider/columes"}}
            """
        cinder_dict = {}
        section_dict = {}
        for line in get_active_lines(context.content):
            if line.startswith("["):
                # new section beginning
                section_dict = {}
                cinder_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, value = line.split("=", 1)
                section_dict[key.strip()] = value.strip()
        return cls(cinder_dict, context.path)


