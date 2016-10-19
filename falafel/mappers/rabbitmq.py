from .. import Mapper, LogFileOutput, mapper


@mapper("rabbitmq_report", ["total_limit"])
def fd_total_limit(context):
    """Deprecated, do not use."""
    for line in context.content:
        if "file_descriptors" in line and "total_limit" in line:
            line_splits = line.replace("}", "").split(",")
            if len(line_splits) > 3:
                return int(line_splits[2])


@mapper("rabbitmq_report", ["total_limit"])
class RabbitMQFileDescriptors(Mapper):

    NO_VALUE = -1

    def parse_content(self, content):
        self.fd_total_limit = self.NO_VALUE
        for line in content:
            if "file_descriptors" in line and "total_limit" in line:
                line_splits = line.replace("}", "").split(",")
                if len(line_splits) > 3:
                    self.fd_total_limit = int(line_splits[2])
                    break


@mapper("rabbitmq_users")
class RabbitMQUsers(Mapper):

    def parse_content(self, content):
        users_dict = {}
        for line in content[1:-1]:
            line_splits = line.split()
            if len(line_splits) > 1:
                users_dict[line_splits[0]] = line_splits[1][1:-1]
        self.data = users_dict


@mapper("rabbitmq_startup_log")
class RabbitMQStartupLog(LogFileOutput):
    pass
