from falafel.core.plugins import mapper


@mapper("cobbler_modules.conf")
def cobbler_modules_conf(context):
    """
    Parses cobbler/modules.conf and returns a dict.
    - {
        "authentication": {"module":"authn_spacewalk"},
        "authorization": {"module":"authz_allowall"}
      }
    """
    modules_dict = {}
    section_dict = {}
    for line in context.content:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        if line.startswith("["):
            # new section beginning
            section_dict = {}
            modules_dict[line[1:-1]] = section_dict
        elif '=' in line:
            key, _, value = line.partition("=")
            section_dict[key.strip()] = value.strip()
    return modules_dict
