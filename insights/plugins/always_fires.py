from insights.core.plugins import make_response, rule


@rule()
def report():
    if True:
        return make_response("ALWAYS_FIRES", kernel="this is junk")
