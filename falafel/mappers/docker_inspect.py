from .. import mapper
from ..core.marshalling import unmarshal

"""
Parse the output of command "docker inspect --type=image" and "docker inspect
--type=cotainer" and return dict.  The output of these two commands is
formatted similiar as json, so "json.loads" function could parse the output
well.
"""


@mapper("docker_image_inspect")
def image(context):
    content = "\n".join(list(context.content))
    inspect_data = unmarshal(content)
    return inspect_data[0]


@mapper("docker_container_inspect")
def container(context):
    content = "\n".join(list(context.content))
    inspect_data = unmarshal(content)
    return inspect_data[0]
