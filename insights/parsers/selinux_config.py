from .. import get_active_lines, Parser, parser
from insights.specs import selinux_config


@parser(selinux_config)
class SelinuxConfig(Parser):

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
