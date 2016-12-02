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
    return _parse(context)


@mapper("docker_container_inspect")
def container(context):
    return _parse(context)


def _parse(context):
    content = "\n".join(list(context.content))
    try:
        inspect_data = unmarshal(content)
        return inspect_data[0]
    except:
        pass
