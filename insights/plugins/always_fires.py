from insights.core.plugins import make_response, rule


@rule(requires=[])
def report(local, shared):
    if True:
        return make_response("ALWAYS_FIRES", kernel="this is junk")
