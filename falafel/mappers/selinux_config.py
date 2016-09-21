from .. import mapper


@mapper("selinux-config")
def parse_selinux_config(context):
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
    for line in context.content:
        line = line.strip()
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result
