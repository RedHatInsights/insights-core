from insights import combiner, rule, make_pass


CONTENT = "This should never display"


@combiner()
def thing():
    raise Exception


@rule(thing)
def report(t):
    return make_pass("THING")
