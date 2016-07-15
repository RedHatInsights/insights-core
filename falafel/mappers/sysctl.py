from falafel.core.plugins import mapper


@mapper('sysctl')
def runtime(context):
    r = {}
    for line in context.content:
        if "=" not in line:
            continue

        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        r[k] = v
    return r
