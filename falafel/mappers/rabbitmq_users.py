from falafel.core.plugins import mapper


@mapper("rabbitmq_users")
def get_users(context):
    users_dict = {}
    for line in context.content[1:-1]:
        line_splits = line.split()
        if len(line_splits) > 1:
            users_dict[line_splits[0]] = line_splits[1][1:-1]
    return users_dict
