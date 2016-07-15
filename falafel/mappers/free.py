from falafel.core.plugins import mapper


@mapper('free')
def free(context):
    parsed = {}

    for line in context.content:
        line = line.strip()
        parts = line.split()
        if line.startswith("Mem:"):
            parsed['total'] = int(parts[1])
        if line.startswith("Swap:"):
            parsed['total_swap'] = int(parts[1])

    return parsed
