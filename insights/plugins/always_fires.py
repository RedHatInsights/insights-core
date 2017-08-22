from insights.core.plugins import make_response, rule


@rule(requires=[])
def report(broker):
    if True:
        return make_response("ALWAYS_FIRES", kernel="this is junk")
