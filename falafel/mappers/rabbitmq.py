from falafel.core.plugins import mapper
from falafel.core import MapperOutput


@mapper("rabbitmq_report", ["total_limit"])
def fd_total_limit(context):
    for line in context.content:
        if "file_descriptors" in line and "total_limit" in line:
            line_splits = line.replace("}", "").split(",")
            if len(line_splits) > 3:
                return int(line_splits[2])


@mapper("rabbitmq_users")
class RabbitMQUsers(MapperOutput):

    @staticmethod
    def parse_content(content):
        users_dict = {}
        for line in content[1:-1]:
            line_splits = line.split()
            if len(line_splits) > 1:
                users_dict[line_splits[0]] = line_splits[1][1:-1]
        return users_dict
