from falafel.core.plugins import mapper


@mapper("docker_sysconfig")
def docker_sysconfig_parser(context):
    """
    This function is used to collect configuration in /etc/sysconfig/docker,
    and store it as key-value type.
    """
    docker_sysconfig = {}
    for line in context.content:
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        (key, value) = line.strip().split("=", 1)
        if "#" in value:
            value = value.strip().split("#", 1)[0].strip()
        docker_sysconfig[key.strip()] = value
    return docker_sysconfig
