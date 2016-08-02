from falafel.core.plugins import mapper


@mapper("rabbitmq_report", ["total_limit"])
def fd_total_limit(context):
    for line in context.content:
        if "file_descriptors" in line and "total_limit" in line:
            line_splits = line.replace("}", "").split(",")
            if len(line_splits) > 3:
                return int(line_splits[2])
