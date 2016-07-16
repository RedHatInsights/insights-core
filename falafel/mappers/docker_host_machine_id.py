from falafel.core.plugins import mapper


@mapper("docker_host_machine-id")
def docker_host_machineid_parser(context):
    content = list(context.content)[0]
    return {"host_system_id": content}
