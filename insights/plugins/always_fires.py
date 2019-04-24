from insights import make_pass, rule


@rule(tags=["test"])
def report():
    if True:
        return make_pass("ALWAYS_FIRES", kernel="this is junk")
