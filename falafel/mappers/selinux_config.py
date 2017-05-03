from .. import get_active_lines, Mapper, mapper


@mapper("selinux-config")
class SelinuxConfig(Mapper):

    def parse_content(self, content):
        """
        parsing selinux-config and return a list(dict).
        Input Example:
            {"hostname" : "elpmdb01a.glic.com",
            "content" : "SELINUX=disabled\n#protection.\nSELINUXTYPE=targeted \n"
            ...
            }
        Output Example:
        [   {'SELINUX': 'disabled',
            'SELINUXTYPE': 'targeted'
            }
        ]
        """
        result = {}
        for line in get_active_lines(content):
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
        self.data = result
