from falafel.core.plugins import mapper


@mapper("hostname")
def common(context):
    hostname = context.content[0].strip()
    return {
        "fqdn": hostname,
        "hostname": hostname.split(".")[0],
        "rhel_release": context.release,
        "rhel_version": context.version
    }
