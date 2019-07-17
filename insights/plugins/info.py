from insights import rule, make_fail, make_pass, make_info


@rule()
def report():
    return make_fail("SOME_FAIL", foo="bar")


@rule()
def report2():
    return make_pass("SOME_PASS", foo="bar")


@rule()
def report3():
    return make_info("SOME_INFO", foo="bar")
