from falafel.core.plugins import mapper


@mapper('systemctl_list-unit-files')
@mapper('chkconfig')
def enabled(context):
    return [line.split()[0] for line in context.content if "enabled" in line or ":on" in line]


def is_enabled(service, shared):
    if enabled in shared:
        enabled_list = shared[enabled]
        return service in enabled_list
    else:
        return False
