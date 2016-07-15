from falafel.core.plugins import mapper

@mapper("docker_info")
def docker_info_parser(context):
    docker_info = {}
# there will be more than 10 lines in the command output if "docker info" command executes successfully.
    if len(context.content) >= 10:
        for line in context.content:
            if ":" in line:
               key, value = line.strip().split(":", 1)
               value = value.strip()
               value = value if value else None
               docker_info[key.strip()] = value
    return docker_info
