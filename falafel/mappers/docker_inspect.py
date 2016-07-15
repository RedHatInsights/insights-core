from falafel.core.plugins import mapper

try:
    import cjson
    json_encode = cjson.encode
    json_decode = cjson.decode
except ImportError:
    import json
    json_encode = json.dumps
    json_decode = json.loads

"""
Parse the output of command "docker inspect --type=image" and "docker inspect --type=cotainer" and return dict.
The output of these two commands is formatted similiar as json, so "json.loads" function could parse the output well.
"""

@mapper("docker_image_inspect")
def docker_image_inspect_parser(context):
    content = "\n".join(list(context.content))
    inspect_data = json_decode(content)
    return inspect_data[0]


@mapper("docker_container_inspect")
def docker_container_inspect_parser(context):
    content = "\n".join(list(context.content))
    inspect_data = json_decode(content)
    return inspect_data[0]
